#!/usr/bin/env node
import {spawn} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {createInterface} from 'node:readline';

const upstream = spawn('npx', ['-y', '@brightdata/mcp'], {
  stdio: ['pipe', 'pipe', 'inherit'],
  env: process.env,
});

const authFile = process.env.CODEX_AUTH_FILE || '/data/lcq/.codex/auth.json';
const llmBaseUrl = process.env.BRIGHTDATA_EXTRACT_LLM_BASE_URL
  || process.env.OPENAI_BASE_URL || 'http://127.0.0.1:20128/v1';
const llmModel = process.env.BRIGHTDATA_EXTRACT_LLM_MODEL
  || process.env.OPENAI_MODEL || 'gpt-5.2';
const unlockerZone = process.env.WEB_UNLOCKER_ZONE || 'mcp_unlocker';

function send(message) {
  process.stdout.write(`${JSON.stringify(message)}\n`);
}

function fail(id, code, message) {
  send({jsonrpc: '2.0', id, error: {code, message}});
}

function apiHeaders(toolName) {
  return {
    authorization: `Bearer ${process.env.API_TOKEN}`,
    'user-agent': '@brightdata/mcp-extract-adapter/1.0.0',
    'x-mcp-tool': toolName,
  };
}

function llmApiKey() {
  if (process.env.BRIGHTDATA_EXTRACT_LLM_API_KEY)
    return process.env.BRIGHTDATA_EXTRACT_LLM_API_KEY;
  if (process.env.OPENAI_API_KEY)
    return process.env.OPENAI_API_KEY;
  try {
    const auth = JSON.parse(readFileSync(authFile, 'utf8'));
    return auth.OPENAI_API_KEY || auth.openai_api_key
      || auth.tokens?.OPENAI_API_KEY;
  } catch {
    return null;
  }
}

function parseChat(text) {
  if (!text.startsWith('data:'))
    return JSON.parse(text).choices?.[0]?.message?.content || text;
  let out = '';
  for (const line of text.split(/\r?\n/)) {
    if (!line.startsWith('data:'))
      continue;
    const data = line.slice(5).trim();
    if (!data || data === '[DONE]')
      continue;
    out += JSON.parse(data).choices?.[0]?.delta?.content || '';
  }
  return out;
}

function jsonOnly(text) {
  const trimmed = text.trim().replace(/^```(?:json)?/i, '')
    .replace(/```$/i, '').trim();
  try {
    return JSON.stringify(JSON.parse(trimmed));
  } catch {}
  const starts = [trimmed.indexOf('{'), trimmed.indexOf('[')]
    .filter(index => index >= 0);
  if (!starts.length)
    throw new Error('LLM extract response did not contain JSON');
  const start = Math.min(...starts);
  const end = Math.max(trimmed.lastIndexOf('}'), trimmed.lastIndexOf(']'));
  return JSON.stringify(JSON.parse(trimmed.slice(start, end + 1)));
}

async function extract({url, extraction_prompt: extractionPrompt}) {
  if (!process.env.API_TOKEN)
    throw new Error('API_TOKEN is required');
  const scrape = await fetch('https://api.brightdata.com/request', {
    method: 'POST',
    headers: {...apiHeaders('extract'), 'content-type': 'application/json'},
    body: JSON.stringify({
      url,
      zone: unlockerZone,
      format: 'raw',
      data_format: 'markdown',
    }),
  });
  const markdown = await scrape.text();
  if (!scrape.ok) {
    throw new Error(
      `Bright Data scrape failed: ${scrape.status} ${markdown.slice(0, 300)}`);
  }
  const key = llmApiKey();
  if (!key)
    throw new Error('No local LLM API key found for extract adapter');
  const system = 'You are a data extraction specialist. You MUST respond with '
    + 'ONLY valid JSON, no other text or formatting. Extract the requested '
    + 'information from the markdown content and return it as a properly '
    + 'formatted JSON object. Do not include any explanations, markdown '
    + 'formatting, or text outside the JSON response.';
  const user = extractionPrompt
    || 'Extract the requested information from this markdown content and return ONLY a JSON object:';
  const chat = await fetch(
    `${llmBaseUrl.replace(/\/$/, '')}/chat/completions`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${key}`,
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        model: llmModel,
        messages: [
          {role: 'system', content: system},
          {
            role: 'user',
            content: `${user}\n\nMarkdown content:\n${markdown}`
              + '\n\nRemember: Respond with ONLY valid JSON, no other text.',
          },
        ],
        temperature: 0,
      }),
    });
  const chatText = await chat.text();
  if (!chat.ok)
    throw new Error(`LLM extract failed: ${chat.status} ${chatText.slice(0, 300)}`);
  return jsonOnly(parseChat(chatText));
}

createInterface({input: upstream.stdout}).on('line', line => {
  if (line.trim())
    process.stdout.write(`${line}\n`);
});

createInterface({input: process.stdin}).on('line', async line => {
  if (!line.trim())
    return;
  let message;
  try {
    message = JSON.parse(line);
  } catch {
    upstream.stdin.write(`${line}\n`);
    return;
  }
  if (message.method === 'tools/call' && message.params?.name === 'extract') {
    try {
      const text = await extract(message.params.arguments || {});
      send({
        jsonrpc: '2.0',
        id: message.id,
        result: {content: [{type: 'text', text}], isError: false},
      });
    } catch (error) {
      fail(message.id, -32000, error.message || String(error));
    }
    return;
  }
  upstream.stdin.write(`${line}\n`);
});

upstream.on('exit', code => process.exit(code ?? 1));
