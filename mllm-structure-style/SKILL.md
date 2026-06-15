---
name: mllm-structure-style
description: MLLM 推理工程架构、评估接入、Hydra 配置工程、既有项目迁移整理与代码风格基础规范。Use when Codex needs to initialize an MLLM inference/evaluation project, scaffold a Hydra + torchrun + strategy-method codebase, migrate an existing unstructured MLLM project into the template layout, design Lightning-Hydra-style config groups without Trainer, integrate VLMEvalKit via adapters, add a new multimodal inference algorithm, or review/refactor MLLM inference/evaluation code for project structure, module boundaries, distributed routing, device placement, experiment logging, and style compliance.
---

# MLLM 推理工程架构与开发规范

## 核心哲学

- 配置驱动：代码中零硬编码。模型路径、硬件、batch size、方法超参、输出路径全部通过 Hydra YAML 注入。
- 原生调度：用 `torchrun` 与 `torch.distributed` 接管控制流，不引入沉重 Trainer 封装。单卡调试与多卡数据并行必须共用同一入口。
- 算法插件化：用 Strategy Pattern 分离模型加载与前向生成算法。新增论文方法必须新增 `src/methods/*.py` 与 `configs/method/*.yaml`，不得修改主干 pipeline。
- 底层优化优先：默认面向 `bfloat16`、`flash_attention_2`、`accelerate` 风格的低内存加载；模板不硬依赖 `flash-attn`，避免初始化被 CUDA 编译环境阻断。

## Scaffold

优先使用本 skill 自带脚手架初始化项目：

```bash
python ~/.codex/skills/mllm-structure-style/scripts/scaffold.py ./mllm-infer-template --name mllm-infer-template
cd ./mllm-infer-template
uv sync
uv run torchrun --nproc_per_node=1 src/infer.py
uv run torchrun --nproc_per_node=2 src/infer.py
uv run torchrun --nproc_per_node=1 src/infer.py experiment=mock_smoke debug=default
```

脚手架会生成可运行 mock inference 管线，用于验证 Hydra 配置、`torchrun`、分布式 gather、插件化 method contract 与代码风格。

## 既有项目迁移整理

当用户已有项目但未按规范组织时，使用“先审计、后迁移、再锁主干”的流程，不要直接在原文件上大规模乱改：

1. 只读审计现状：

```bash
python ~/.codex/skills/mllm-structure-style/scripts/audit_existing_project.py ~/path/to/existing-project
```

2. 生成或确认目标骨架：若项目缺少模板基础，先在临时目录 scaffold 一份标准模板，对照迁移；若要原地迁移，先确认不会覆盖用户文件。
3. 建立迁移映射表：把现有文件按职责归入 `src/data`、`src/models`、`src/methods`、`src/adapters`、`src/utils`、`configs/*`、`scripts/*`。
4. 抽离硬编码：模型路径、数据路径、batch size、dtype、device、输出路径、评估数据集全部移动到 Hydra YAML。
5. 稳定入口：最终只保留 `src/infer.py` 作为纯推理指挥官，`src/eval.py` 作为评估指挥官；旧入口脚本只能变成 `scripts/*.sh` 或 `configs/experiment/*.yaml`。
6. 逐步验收：先 mock/小样本跑通，再接真实模型，再接 VLMEvalKit，不一次性重写全部算法。

迁移映射规则：

- 旧 `Dataset`、json/csv/parquet 读取、样本枚举 -> `src/data`；若夹带 tokenizer/processor，拆到 method 或 model runtime。
- 旧 `AutoModel/AutoProcessor/from_pretrained`、量化、权重加载 -> `src/models` wrapper；必须 lazy `setup(device)`。
- 旧 `generate()`、beam search、特征提取、论文复现逻辑 -> `src/methods`；继承 `BaseMethod`，适配 `generate(batch)`。
- 旧 argparse/YAML/global constants -> `configs/*`；入口改 Hydra defaults + CLI override。
- 旧多卡/DDP/all_gather/device 逻辑 -> `src/utils/dist_utils.py` 或由 `src/infer.py` 编排。
- 旧评估脚本/benchmark glue -> `src/adapters` + `src/eval.py`；不要塞进 `methods` 或 `models`。
- 旧 shell 命令、部署启动命令 -> `scripts/`；不要把环境变量和路径写死在 Python 中。

迁移期间必须保护用户代码：

- 不删除旧实现，除非用户明确要求；先移动/包装/适配。
- 不把旧项目的训练逻辑塞入推理模板；训练应另建边界。
- 不为迁移方便修改 `BaseMethod` 合约，除非所有现有方法和测试同步更新。
- 每迁移一个模块就补一个最小测试，防止“整理完但不能跑”。

## 目录标准

项目必须保持以下职责边界：

```text
mllm-infer-template/
├── configs/
│   ├── data/          # 数据集与 DataLoader 参数
│   ├── model/         # MLLM 加载参数，不包含解码逻辑
│   ├── method/        # 前向生成算法参数
│   ├── eval_tasks/    # VLMEvalKit benchmark 列表与评估参数
│   ├── paths/         # 输出路径
│   ├── env/           # 分布式与硬件参数
│   ├── hydra/         # Hydra 日志、run/multirun 目录
│   ├── extras/        # warnings、配置树打印、tag 校验
│   ├── logger/        # null/jsonl/wandb 实验记录器
│   ├── debug/         # 单机调试覆盖
│   ├── experiment/    # 可复现实验覆盖
│   ├── local/         # 个人机器私有配置，不提交 git
│   ├── hparams_search/# Hydra sweeper/Optuna 示例
│   ├── infer.yaml     # 推理入口拼装配置
│   └── eval.yaml      # 评估入口拼装配置
├── scripts/
│   ├── run_single.sh  # 单卡调试推理
│   ├── run_dist.sh    # 多卡 torchrun 推理
│   ├── run_infer.sh   # 统一推理别名
│   └── run_eval.sh    # VLMEvalKit 评估入口
├── src/
│   ├── adapters/      # 外部评估/服务框架桥接层
│   ├── data/          # 只读数据，输出原生 dict 或 Tensor
│   ├── models/        # 权重加载、lazy setup、生命周期管理
│   ├── methods/       # BaseMethod 与论文算法策略
│   ├── utils/         # 分布式、日志、实例化工具
│   ├── infer.py       # 纯推理 Pipeline 指挥官
│   └── eval.py        # 评估 Pipeline 指挥官
└── pyproject.toml     # uv 依赖定义
```

## 模块边界

- `src/data`：只把磁盘数据转成 Python `dict` 或 PyTorch `Tensor`。禁止在 Dataset 中做 tokenization、processor、模型特定图像处理。
- `src/models`：只管理模型权重安全加载与生命周期。Wrapper 必须 lazy initialization：`__init__` 仅绑定配置，`setup(device)` 才执行加载与显式 device placement。
- 真实 Hugging Face 模型适配优先参考 `src/models/hf.py`：`from_pretrained` 参数必须来自 YAML，`torch_dtype`、`attn_implementation`、`low_cpu_mem_usage`、`device_map` 必须显式可配；`setup(device)` 内完成加载与 `.to(device)`。
- `src/methods`：承载所有论文方法、特征提取、特殊解码策略。所有新增算法继承 `BaseMethod`，通过统一 `generate(batch) -> list[dict]` 输出。
- `src/infer.py`：唯一编排层。只负责 Hydra 配置、对象实例化、单/多卡感知、sampler 分片、循环推理、`all_gather_object` 与 Rank 0 输出。
- `src/adapters`：唯一允许接入外部评估/服务框架的位置。VLMEvalKit、服务框架、benchmark 框架都只能在这里翻译 I/O，不得反向污染 `src/models`、`src/methods`、`src/infer.py`。
- `src/eval.py`：评估编排层。复用 `model`/`method` 配置与分布式控制，把模型和算法包装成 VLMEvalKit `BaseModel`，由 VLMEvalKit 负责 benchmark prompt、结果落盘、指标计算。

## Hydra 配置工程规范

- 借鉴 Lightning-Hydra Template 的配置分组：采用 `extras`、`paths`、`hydra`、`debug`、`experiment`、`local`、`hparams_search`、`logger`。
- 禁止引入 Lightning `Trainer`、`callbacks`、Lightning logger 抽象；本工程仍由 `torchrun`、`torch.distributed`、`infer.py`、`eval.py` 原生编排。
- `configs/hydra/default.yaml` 统一 run/multirun 目录与 colorlog：输出落在 `${paths.log_dir}/${task_name}/...`。
- `configs/extras/default.yaml` 控制配置树打印、warnings、tag 校验；默认不交互式询问 tags，避免多卡任务卡死。
- `configs/experiment/*.yaml` 只写可复现实验覆盖，不写个人路径；个人路径写入 `configs/local/default.yaml`，该文件不提交 git。
- `configs/logger/*.yaml` 只配置轻量实验记录器：默认 `null`，可选 `jsonl`，`wandb` 需安装 `tracking` extra。
- `configs/hparams_search/*.yaml` 仅作为 Hydra sweeper 示例；Optuna 需安装 `sweeper` extra。

常用命令：

```bash
uv run torchrun --nproc_per_node=1 src/infer.py experiment=mock_smoke
uv run torchrun --nproc_per_node=1 src/infer.py experiment=mock_smoke debug=default
uv run torchrun --nproc_per_node=1 src/infer.py logger=jsonl tags='[paper_x,ablation]'
uv sync --extra tracking && uv run torchrun --nproc_per_node=1 src/infer.py logger=wandb
uv sync --extra sweeper && uv run python src/eval.py -m hparams_search=method_optuna
```

## 强制风格

- 必须写完整类型注解，尤其是函数签名、复杂类属性、batch/result 结构。
- 禁止 `print()`。使用 `logging.getLogger(__name__)`，普通进度日志仅 Rank 0 输出。
- 禁止 `.cuda()`。通过 `dist_utils.get_device()` 获取当前进程设备，再显式 `.to(device)`。
- 禁止硬编码路径、模型名、batch size、dtype、输出路径、rank/world size。
- 禁止为了适配算法修改 `src/infer.py`。算法适配统一 method 接口，不让 pipeline 适配算法。
- 禁止把 VLMEvalKit 逻辑写进 `src/methods` 或 `src/models`；外部框架差异必须封装在 adapter。
- 命名：类用 `PascalCase`，函数/变量用 `snake_case`，常量用 `UPPER_SNAKE_CASE`。

## 新增算法流程

1. 在 `src/methods/` 新建文件，如 `paper_xyz.py`，继承 `BaseMethod`。
2. 在 `configs/method/` 新建 `paper_xyz.yaml`，`_target_` 指向新类。
3. 直接覆盖配置运行，不改主干：

```bash
uv run torchrun --nproc_per_node=2 src/infer.py method=paper_xyz
```

新增方法必须通过 `uv run pytest -q`，并补充至少一个 method contract 测试。

## 真实模型接入

默认 scaffold 使用 mock 模型避免下载权重。接入真实 MLLM 时，新增或修改 `configs/model/*.yaml` 指向 `models.hf.HFMLLMWrapper`：

```yaml
_target_: models.hf.HFMLLMWrapper
path: ~/path/to/model
torch_dtype: bfloat16
attn_implementation: flash_attention_2
low_cpu_mem_usage: true
device_map: null
trust_remote_code: true
```

运行时仍保持同一入口：

```bash
uv run torchrun --nproc_per_node=2 src/infer.py model=hf
```

## VLMEvalKit 评估接入

模板通过 Adapter Pattern 集成 VLMEvalKit：

- 依赖包名：PyPI 使用 `ms-vlmeval`，Python import 使用 `vlmeval`。
- 默认兼容解固定为稳定 Hydra 轨道：`hydra-core==1.3.2`、`omegaconf==2.3.0`、`transformers>=4.41,<4.52`、`ms-vlmeval==0.0.19`；`ms-vlmeval` 放在 `eval` optional extra 中，使用 `uv sync --extra eval` 安装。
- Hydra 工具依赖：默认安装 `hydra-colorlog==1.2.0`、`rich`、`python-dotenv`、`rootutils`；`wandb` 与 `hydra-optuna-sweeper` 分别放在 `tracking`、`sweeper` optional extras 中。
- 不要默认升级到 `ms-vlmeval==0.0.20`：该版本强制 `omegaconf>=2.4.0.dev4`、`antlr4-python3-runtime==4.11.1`、`polygon3`，会与 Hydra 1.3 stable 的 `omegaconf<2.4`、`antlr4==4.9.*` 冲突，并可能触发本地 C 扩展编译问题。
- 不要让 resolver 升到 `transformers>=4.52`：VLMEvalKit 0.0.19 仍引用 `AutoModelForVision2Seq`，该导出在 4.52+ 不再可用。
- `src/adapters/vlmeval_adapter.py` 继承 `vlmeval.vlm.base.BaseModel`，实现 `generate_inner(message, dataset=None)`。
- Adapter 将 VLMEvalKit message 翻译为本框架 method contract：`{"records": [{"id": ..., "prompt": ..., "image_path": ...}]}`。
- `src/eval.py` 复用 Hydra `model` 和 `method`，调用 VLMEvalKit `build_dataset()`、`infer_data_job()`、`dataset.evaluate()`。
- `src/infer.py` 保持纯推理入口，不引入 benchmark/metric 逻辑。

运行示例：

```bash
uv sync --extra eval
uv run torchrun --nproc_per_node=2 src/eval.py eval_tasks.datasets='[MMBench_DEV_EN]' model=hf
```

需要 LLM-as-judge 的 benchmark 时，通过环境变量或 `configs/eval_tasks/*.yaml` 显式配置 judge 参数，不要在代码中硬编码 API key。
