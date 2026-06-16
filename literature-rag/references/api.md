# Demo RAG API Notes

Use only for token extraction or low-level stream debugging. The normal workflow should use `scripts/demo_chat.py`.

## Auth

- Demo token: browser `localStorage.auth_token` after Google login at `https://demo.rag.ac.cn`.
- Env: `RAG_DEMO_TOKEN=<token>`
- Header: `Authorization: Bearer <RAG_DEMO_TOKEN>`
- 401/403: expired or invalid token. 502: wrong token class or backend issue.

## Token Bookmarklet

Open logged-in `https://demo.rag.ac.cn`, then run:

```text
javascript:(()=>{const t=localStorage.getItem('auth_token');if(!t){alert('No localStorage.auth_token found. Open https://demo.rag.ac.cn/login and sign in first.');return;}document.body.innerHTML='<main style="font:16px/1.5 sans-serif;padding:24px;max-width:900px;margin:auto"><h1>demo.rag.ac.cn token</h1><p>Copy this value into Codex as RAG_DEMO_TOKEN:</p><textarea autofocus style="width:100%;height:160px">'+t.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))+'</textarea></main>';})()
```

If pasted JavaScript is stripped, create a bookmark with this URL and click it on the logged-in page.

## Chat Stream

`POST https://demo.rag.ac.cn/api/chat/stream`

```json
{
  "query": "请帮我找到和resnet相关的24-26年的论文",
  "history": [],
  "effort": "thorough"
}
```

SSE lines start with `data: ` and contain JSON. Observed event types:

- `thinking`, `thinking_delta`, `thinking_content`
- `sql_start`, `sql_retry`, `sql_done`
- `answer_start`, `token`, `done`, `error`

Effort values: `quick`, `balanced`, `thorough`. `demo_chat.py` defaults to `thorough`.
