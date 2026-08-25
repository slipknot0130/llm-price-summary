# LLM Price Summary · One-Click Pricing for All Large Language Models

> A **zero-dependency** local Python tool that compiles the **subscription / plan prices** and **API token prices** of mainstream Large Language Models (LLMs) into a single Markdown file.
> **Core guarantee: by default every run fetches the latest prices live from an online dataset, so you always see up-to-date prices instead of stale cached data.**

---

## 💡 Why This Project

This project was created so that everyone can **get the pricing rules of mainstream LLMs simply and quickly**. There are similar tools on GitHub, but many of them are either no longer maintained or stuck with hardcoded price tables that can never be updated automatically — so when you open them, the models are still last year's versions and the prices no longer match reality.

The goal here is simple: **when you want to check the latest pricing at the first moment, one click gets you the freshest numbers, without visiting every vendor's site one by one**. By default every run fetches the latest prices live from an online dataset — that is what "one-click query" truly means.

---

## ✨ Features

- **Live fetch by default**: Running `python main.py` **always** pulls the latest token prices from the community-maintained LiteLLM dataset and regenerates the summary. Only `--no-update` (offline emergency) uses the local cache, and it prints a prominent warning.
- **Dual price system**: Covers both **subscription / plan prices** (ChatGPT Plus, Claude Pro, Gemini AI Pro, etc.) and **API pay-as-you-go token prices**.
- **Peak / off-peak pricing**: For time-of-day priced models like DeepSeek, a dedicated **peak / off-peak / cache-hit** column layout makes the price gap obvious (synced with the official 2026-08-17 repricing; weekends use off-peak all day).
- **Offline fallback**: The online dataset is cached locally; `--no-update` still works offline (requires at least one prior online run).
- **Zero dependencies**: Standard library only — **no `pip install` needed**.
- **Cross-platform**: Windows / macOS / Linux, Python 3.8+.
- **Easy to extend**: Add/remove models via `watchlist.json`; tweak subscription / peak-off-peak prices via two JSON files.

---

## 📊 Data Sources

| Category | Source | Notes |
| --- | --- | --- |
| Token prices | [LiteLLM `model_prices_and_context_window.json`](https://github.com/BerriAI/litellm) | Community-maintained, covers OpenAI / Anthropic / Google / DeepSeek / Qwen / Kimi / xAI / Llama / Mistral and thousands more |
| Subscription / peak-off-peak | Curated from vendor official sites | Stored in local config files for easy correction |

> 🔄 The dataset is **live**: the LiteLLM repo is continuously updated, and `python main.py` pulls the newest version by default, so the token prices shown always track upstream.

---

## 🤖 Models Covered (continuously updated)

> These are the 2026 mainstream models tracked by `watchlist.json` by default; edit the file to add or remove any model.

- **OpenAI**: GPT-5.5, GPT-5.5 Pro, GPT-5.4, GPT-5 mini, GPT-5 nano, o3, o4-mini
- **Anthropic**: Claude Opus 4.5, Claude Sonnet 4.5, Claude Haiku 4.5, Claude Fable 5
- **Google**: Gemini 3.5 Flash, Gemini 3 Pro, Gemini 3 Flash, Gemini 2.5 Pro, Gemini 2.5 Flash
- **DeepSeek**: V4-Flash, V4-Pro (peak/off-peak)
- **Alibaba Qwen**: Qwen-Max, Qwen-Plus, Qwen-Turbo
- **Moonshot**: Kimi K3, Kimi (latest)
- **xAI**: Grok 4
- **Meta**: Llama 4 Maverick, Llama 4 Scout
- **Mistral**: Mistral Large, Mistral Medium

---

## 📁 Project Structure

```
.
├── main.py                  # Entry: python main.py = fetch latest + generate
├── fetch_prices.py          # Fetch / cache the LiteLLM dataset, normalize by watchlist
├── generate_md.py           # Merge subscription + token prices, render Markdown
├── watchlist.json           # Models to track (add/remove freely)
├── subscription.json        # Subscription / plan prices (manually maintained)
├── pricing_overrides.json   # Peak-off-peak / special pricing (manually maintained)
├── model_prices_cache.json  # Local cache of the online dataset (auto-updated, offline fallback)
└── LLM价格汇总.md           # Final artifact (auto-generated)
```

---

## 🚀 Quick Start

### Requirements
Just **Python 3.8+**. No third-party libraries.

### Three steps

```bash
# 1. Clone the repo
git clone https://github.com/slipknot0130/llm-price-summary.git
cd llm-price-summary

# 2. Fetch the latest prices and generate the summary (live by default)
python main.py          # Windows may use py main.py; macOS/Linux may use python3 main.py

# 3. Open the generated LLM价格汇总.md
```

---

## 🛠 Usage

Three run modes:

```bash
python main.py            # [default] fetch latest prices online + regenerate LLM价格汇总.md
python main.py --update   # only refresh the online price cache (no md regeneration)
python main.py --no-update# offline emergency: generate md from local cache only (warns that data may be stale)
```

> ⚠️ **To get the latest prices, simply re-run `python main.py`** — it fetches live data by default, no extra steps required.

The generated `LLM价格汇总.md` contains:

1. **Subscription / plan price table**: plans, monthly fee, and included quota per vendor.
2. **Token price table (API pay-as-you-go)**: grouped by vendor, normalized to **per 1M tokens** for easy comparison; includes context window and cache-hit price. Peak/off-peak models (DeepSeek) get dedicated peak/off-peak columns.
3. **Usage notes**: the three commands are appended automatically.

### Add / remove tracked models
Edit `watchlist.json`. Each entry looks like:

```json
{
  "provider": "OpenAI",
  "display": "GPT-5.5",
  "litellm_key": "gpt-5.5"
}
```

- `provider`: vendor group name (decides which section it lands in).
- `display`: name shown in the table.
- `litellm_key`: the exact model key in the LiteLLM dataset (search `model_prices_cache.json` to confirm; many keys carry a vendor prefix such as `anthropic.`, `dashscope/`, `deepinfra/meta-llama/`).

### Edit subscription / peak-off-peak prices
- Subscription plans → edit `subscription.json`.
- Peak-off-peak / special pricing (e.g. DeepSeek) → edit `pricing_overrides.json` (see the in-file example with `peak` / `offpeak` / `cache_hit_input` / `window` fields).

---

## ⏱ Peak / Off-peak Pricing (DeepSeek example)

In `pricing_overrides.json`, the DeepSeek V4 series is maintained in official RMB pricing (the **peak/off-peak rules effective 2026-08-17**):

| Model | Peak In | Peak Out | Off-peak In | Off-peak Out | Cache-hit In | Discount Window |
| --- | --- | --- | --- | --- | --- | --- |
| DeepSeek-V4-Flash | ¥3 / 1M | ¥9 / 1M | ¥1.5 / 1M | ¥4.5 / 1M | ¥0.1 / 1M | Weekday off-peak (outside 9–12, 14–18) + all weekend |
| DeepSeek-V4-Pro | ¥9 / 1M | ¥27 / 1M | ¥4.5 / 1M | ¥13.5 / 1M | ¥0.3 / 1M | Same; peak = weekdays 9:00–12:00, 14:00–18:00 (Beijing time) |

To add another peak/off-peak model, add `"override": "corresponding-key"` to its `watchlist.json` entry and maintain the fields in `pricing_overrides.json`.

---

## ⚠️ Data Reliability & Disclaimer

- Token prices are pulled automatically from the LiteLLM public dataset, **subject to that dataset's updates** (latest on every run).
- A few models (e.g. Zhipu GLM, Qwen3) have **no reliable price field** in the public dataset. To avoid presenting fake data, they are marked "see official site" only in the subscription table. To fill them in, add a reference price to `pricing_overrides.json` with an `override` field.
- Subscription prices are approximate values curated from official sites (with rough ¥ conversion) and are for reference only.
- **Always refer to each vendor's official real-time pricing.** This repo is not liable for any loss caused by price discrepancies.

---

## 🔧 Advanced: Windows / macOS Double-click Launchers (optional)

**Windows** — create `更新价格.bat`:
```bat
@echo off
cd /d "%~dp0"
python main.py
start "" "LLM价格汇总.md"
pause
```

**macOS** — create `更新价格.command`:
```bash
#!/bin/bash
cd "$(dirname "$0")"
python3 main.py
open "LLM价格汇总.md"
```
Make it executable: `chmod +x 更新价格.command`.

---

## 📄 License

Released under the [MIT License](./LICENSE).
