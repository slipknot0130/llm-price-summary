# LLM 价格汇总 · 一键查询所有大语言模型定价

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-None-brightgreen.svg)](./requirements.txt)
[![Live Data](https://img.shields.io/badge/Data-Live%20Fetch-orange.svg)](https://github.com/BerriAI/litellm)
[![Models Covered](https://img.shields.io/badge/Models-28%20%7C%202026-blueviolet.svg)](./watchlist.json)

> 一个**零依赖**的本地 Python 小工具：把市面上主流大语言模型（LLM）的 **订阅 / 套餐价** 与 **API Token 价** 汇总成一份 Markdown 文件。
> **核心保证：默认每次运行都实时从在线数据集拉取最新价格，你查到的永远是最新价，不会一直用旧数据。**

---

## 💡 项目初衷

这个项目开发的初衷，就是为了让大家能够**简单、快速地获取主流 LLM 的定价规则**。GitHub 社区里其实也有不少类似的程序，但其中不少要么早就不再更新，要么依赖写死的价格表、根本没有办法自动更新——结果就是大家打开一看，模型还是一年前的老款，价格早就对不上了。

所以本程序的目的很纯粹：**当你想第一时间查到最新定价时，点一下查询就能拿到最新的结果，而不用挨个去各家官网翻**。默认每次运行都实时从在线数据集拉取最新价，这才是「一键查询」真正的意义。

---

## ✨ 功能特性

- **默认实时拉取最新价**：运行 `python main.py` **每次都**从社区维护的公开数据集 LiteLLM 拉取最新 Token 价格并重新生成汇总。只有显式使用 `--no-update`（断网应急）才会用本地缓存，且会给出醒目警告。
- **双价体系**：同时覆盖「订阅 / 套餐价」（ChatGPT Plus / Claude Pro / Gemini AI Pro 等）与「API 按量 Token 价」。
- **峰谷计费**：对 DeepSeek 这类分时计价模型，单独列出 **峰时 / 谷时 / 缓存命中** 价格，一眼看清价差（已同步 2026-08-17 官方调价，周末全天按低谷价）。
- **离线兜底**：本地会自动缓存在线数据集，断网时可用 `--no-update` 生成（需至少联网运行过一次）。
- **零依赖**：只使用 Python 标准库，**无需 `pip install`**。
- **跨平台**：Windows / macOS / Linux 通用，Python 3.8+ 即可。
- **易扩展**：增删模型只改 `watchlist.json`；改订阅价 / 峰谷价只改两个 JSON 文件。

---

## 📊 数据来源

| 类别 | 来源 | 说明 |
| --- | --- | --- |
| Token 价格 | [LiteLLM `model_prices_and_context_window.json`](https://github.com/BerriAI/litellm) | 社区长期维护，覆盖 OpenAI / Anthropic / Google / DeepSeek / 通义 / Kimi / xAI / Llama / Mistral 等数千模型 |
| 订阅 / 峰谷价格 | 各厂商官网整理 | 存于本地配置文件，便于自行校正 |

> 🔄 数据集是**活的**：LiteLLM 仓库持续更新，`python main.py` 默认拉的就是最新版，因此本工具展示的 Token 价始终跟随上游。

---

## 🤖 当前覆盖的模型（持续更新）

> 以下为 `watchlist.json` 默认追踪的 2026 年主流模型；如需增删，编辑该文件即可。

- **OpenAI**：GPT-5.5、GPT-5.5 Pro、GPT-5.4、GPT-5 mini、GPT-5 nano、o3、o4-mini
- **Anthropic**：Claude Opus 4.5、Claude Sonnet 4.5、Claude Haiku 4.5、Claude Fable 5
- **Google**：Gemini 3.5 Flash、Gemini 3 Pro、Gemini 3 Flash、Gemini 2.5 Pro、Gemini 2.5 Flash
- **DeepSeek**：V4-Flash、V4-Pro（峰谷计费）
- **阿里通义**：Qwen-Max、Qwen-Plus、Qwen-Turbo
- **Moonshot**：Kimi K3、Kimi (latest)
- **xAI**：Grok 4
- **Meta**：Llama 4 Maverick、Llama 4 Scout
- **Mistral**：Mistral Large、Mistral Medium

---

## 📁 目录结构

```
.
├── main.py                  # 入口：python main.py = 在线拉取最新价 + 生成
├── fetch_prices.py          # 拉取 / 缓存 LiteLLM 数据集，按 watchlist 归一化
├── generate_md.py           # 合并订阅 + Token 价，渲染 Markdown
├── watchlist.json           # 要追踪的主力模型清单（可增删）
├── subscription.json        # 订阅 / 套餐价（手动维护）
├── pricing_overrides.json   # 峰谷计费 / 特殊定价（手动维护）
├── model_prices_cache.json  # 在线数据集本地缓存（自动更新，离线兜底）
└── LLM价格汇总.md           # 最终产物（自动生成）
```

---

## 🚀 快速开始

### 环境要求
只需安装 **Python 3.8 或以上**，无需任何第三方库。

### 三步上手

```bash
# 1. 克隆本仓库
git clone https://github.com/slipknot0130/llm-price-summary.git
cd llm-price-summary

# 2. 一键拉取最新价格并生成汇总（默认即在线实时拉取）
python main.py          # Windows 可能是 py main.py；macOS/Linux 可能是 python3 main.py

# 3. 打开生成的 LLM价格汇总.md 查看
```

---

## 🛠 使用说明

程序提供三种运行模式：

```bash
python main.py            # 【默认】在线拉取最新价格 + 重新生成 LLM价格汇总.md
python main.py --update   # 仅刷新在线价格缓存（不重新生成 md）
python main.py --no-update# 断网应急：仅用本地缓存生成 md（会显式警告数据可能过时）
```

> ⚠️ **想拿到最新价，直接重跑 `python main.py` 即可**——它默认就联网取最新数据，不需要额外操作。

生成的 `LLM价格汇总.md` 包含：

1. **订阅 / 套餐价格表**：按厂商列出套餐、月费、包含额度。
2. **Token 价格表（API 按量）**：按厂商分组，统一换算为「每百万 (1M) tokens」计价，便于横向对比；含上下文窗口、缓存命中价。凡有峰谷计费的模型（DeepSeek）单独列出峰时 / 谷时多列。
3. **使用说明**：脚本自动附录三条运行命令。

### 增删追踪的模型
编辑 `watchlist.json`，每个条目形如：

```json
{
  "provider": "OpenAI",
  "display": "GPT-5.5",
  "litellm_key": "gpt-5.5"
}
```

- `provider`：厂商分组名（决定 Markdown 中归到哪一节）。
- `display`：表格里显示的名称。
- `litellm_key`：LiteLLM 数据集中的精确模型 key（可在 `model_prices_cache.json` 中搜索确认，注意很多 key 带厂商前缀，如 `anthropic.`、`dashscope/`、`deepinfra/meta-llama/`）。

### 修改订阅价 / 峰谷价
- 订阅套餐价 → 编辑 `subscription.json`。
- 峰谷 / 特殊定价（如 DeepSeek）→ 编辑 `pricing_overrides.json`，结构见文件内示例（含 `peak` / `offpeak` / `cache_hit_input` / `window` 字段）。

---

## ⏱ 峰谷计费（以 DeepSeek 为例）

`pricing_overrides.json` 中，DeepSeek V4 系列按官方人民币计价单独维护（**2026-08-17 起生效的峰谷规则**）：

| 模型 | 峰时输入 | 峰时输出 | 谷时输入 | 谷时输出 | 缓存命中输入 | 优惠时段 |
| --- | --- | --- | --- | --- | --- | --- |
| DeepSeek-V4-Flash | ¥3 / 1M | ¥9 / 1M | ¥1.5 / 1M | ¥4.5 / 1M | ¥0.1 / 1M | 工作日低谷（非 9–12、14–18 点）+ 周末全天 |
| DeepSeek-V4-Pro | ¥9 / 1M | ¥27 / 1M | ¥4.5 / 1M | ¥13.5 / 1M | ¥0.3 / 1M | 同上；高峰为工作日 9:00–12:00、14:00–18:00（北京时间） |

当你新增一个有峰谷计费的模型时，在 `watchlist.json` 里给该条目加 `"override": "对应key"`，并在 `pricing_overrides.json` 中维护对应字段即可。

---

## ⚠️ 数据可靠性与免责声明

- 本工具的 Token 价格自动取自 LiteLLM 公开数据集，**以源数据集更新为准**（运行即拉最新）。
- 智谱 GLM、Qwen3 等个别模型在公开数据集中**暂无可靠价格字段**，为避免提供假数据，这类模型仅在订阅表标注「以官网为准」。如需补全，请往 `pricing_overrides.json` 添加参考价并设 `override` 字段。
- 订阅价为官网整理的近似值（含约 ¥ 换算），仅供参考。
- **一切以各厂商官网实时报价为准。** 本仓库不对因价格偏差造成的损失负责。

---

## 🔧 进阶：Windows / macOS 双击启动器（可选）

不想敲命令，可以自建启动器：

**Windows** — 新建 `更新价格.bat`，内容：
```bat
@echo off
cd /d "%~dp0"
python main.py
start "" "LLM价格汇总.md"
pause
```

**macOS** — 新建 `更新价格.command`，内容：
```bash
#!/bin/bash
cd "$(dirname "$0")"
python3 main.py
open "LLM价格汇总.md"
```
并赋予执行权限：`chmod +x 更新价格.command`。

---

## 📄 许可证

本项目基于 [MIT License](./LICENSE) 开源。

---

## ⭐ 支持这个项目

如果这个工具帮到了你，欢迎 **Star ⭐** 本仓库——你的每一个 Star 都是对持续维护的最大鼓励！

觉得哪里可以更好？欢迎提 [Issue](https://github.com/slipknot0130/llm-price-summary/issues) 或 [Pull Request](https://github.com/slipknot0130/llm-price-summary/pulls)，一起让这份价格表更准、更全。
