# LLM 价格汇总 · 一键查询所有大语言模型定价

> 一个**零依赖**的本地 Python 小工具：把市面上主流大语言模型（LLM）的 **订阅 / 套餐价** 与 **API Token 价** 汇总成一份 Markdown 文件，并支持「一键更新最新价格」，让你第一时间拿到各家最新报价。

---

## ✨ 功能特性

- **一键更新**：运行一条命令，即从社区维护的公开数据集拉取最新 Token 价格并重新生成汇总。
- **双价体系**：同时覆盖「订阅 / 套餐价」（ChatGPT Plus、Claude Pro、Gemini Advanced 等）与「API 按量 Token 价」。
- **峰谷计费**：对 DeepSeek 这类分时计价模型，单独列出 **峰时 / 谷时 / 缓存命中** 价格，一眼看清夜间优惠价差。
- **离线兜底**：内置 1.8MB 价格缓存，**断网也能生成汇总**。
- **零依赖**：只使用 Python 标准库，**无需 `pip install`**。
- **跨平台**：Windows / macOS / Linux 通用，Python 3.8+ 即可。
- **易扩展**：增删模型只改 `watchlist.json`；改订阅价 / 峰谷价只改两个 JSON 文件。

---

## 📊 数据来源

| 类别 | 来源 | 说明 |
| --- | --- | --- |
| Token 价格 | [LiteLLM `model_prices_and_context_window.json`](https://github.com/BerriAI/litellm) | 社区长期维护，覆盖 OpenAI / Anthropic / Google / DeepSeek / 通义 / Kimi / GLM / Llama / Mistral 等上千模型 |
| 订阅 / 峰谷价格 | 各厂商官网整理 | 存于本地配置文件，便于自行校正 |

---

## 📁 目录结构

```
.
├── main.py                  # 入口：python main.py = 更新 + 生成
├── fetch_prices.py          # 拉取 / 缓存 LiteLLM 数据集，按 watchlist 归一化
├── generate_md.py           # 合并订阅 + Token 价，渲染 Markdown
├── watchlist.json           # 要追踪的主力模型清单（可增删）
├── subscription.json        # 订阅 / 套餐价（手动维护）
├── pricing_overrides.json   # 峰谷计费 / 特殊定价（手动维护）
├── model_prices_cache.json  # 在线数据集快照（离线兜底，自动更新）
└── LLM价格汇总.md           # 最终产物（自动生成）
```

---

## 🚀 快速开始

### 环境要求
只需安装 **Python 3.8 或以上**，无需任何第三方库。

### 三步上手

```bash
# 1. 克隆本仓库
git clone https://github.com/<你的用户名>/llm-price-summary.git
cd llm-price-summary

# 2. 一键更新最新价格并生成汇总
python main.py          # Windows 可能是 py main.py；macOS/Linux 可能是 python3 main.py

# 3. 打开生成的 LLM价格汇总.md 查看
```

---

## 🛠 使用说明

程序提供三种运行模式（三个命令通用）：

```bash
python main.py            # 更新在线价格缓存 + 重新生成 LLM价格汇总.md
python main.py --update   # 仅刷新在线价格缓存（不重新生成 md）
python main.py --no-update# 断网时，仅用本地缓存生成 md
```

生成的 `LLM价格汇总.md` 包含：

1. **订阅 / 套餐价格表**：按厂商列出套餐、月费、包含额度。
2. **Token 价格表（API 按量）**：按厂商分组，统一换算为「每百万 (1M) tokens」计价，便于横向对比；含上下文窗口、缓存命中价。凡有峰谷计费的模型（DeepSeek）单独列出峰时 / 谷时多列。
3. **使用说明**：脚本自动附录三条运行命令。

### 增删追踪的模型
编辑 `watchlist.json`，每个条目形如：

```json
{
  "provider": "OpenAI",
  "display": "GPT-4o",
  "litellm_key": "gpt-4o"
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

`pricing_overrides.json` 中，DeepSeek 系列按官方人民币计价单独维护：

| 模型 | 峰时输入 | 峰时输出 | 谷时输入 | 谷时输出 | 缓存命中输入 | 优惠时段 |
| --- | --- | --- | --- | --- | --- | --- |
| DeepSeek-V3 | ¥1 / 1M | ¥2 / 1M | ¥0.5 / 1M | ¥1 / 1M | ¥0.1 / 1M | 北京时间 00:30–08:30 |
| DeepSeek-R1 | ¥4 / 1M | ¥16 / 1M | ¥1 / 1M | ¥4 / 1M | ¥1 / 1M | 北京时间 00:30–08:30 |

当你新增一个有峰谷计费的模型时，在 `watchlist.json` 里给该条目加 `"override": "对应key"`，并在 `pricing_overrides.json` 中维护对应字段即可。

---

## ⚠️ 数据可靠性与免责声明

- 本工具的 Token 价格自动取自 LiteLLM 公开数据集，**以源数据集更新为准**。
- 字节豆包、智谱 GLM-4-Plus 等个别模型在公开数据集中**暂无可靠价格字段**，为避免提供假数据，这类模型仅在订阅表标注「以官网为准」。如需补全，请往 `pricing_overrides.json` 添加人民币参考价并设 `override` 字段。
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
