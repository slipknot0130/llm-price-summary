# LLM Price Summary · One-Click Pricing for All Major LLMs

> A **zero-dependency** local Python tool that consolidates the **subscription / plan prices** and **API token prices** of mainstream large language models (LLMs) into a single Markdown file, with a "one-click update" to always get the latest pricing.

---

## ✨ Features

- **One-click update**: Run a single command to fetch the latest token prices from a community-maintained public dataset and regenerate the summary.
- **Dual pricing**: Covers both **subscription / plan prices** (ChatGPT Plus, Claude Pro, Gemini Advanced, etc.) and **API pay-as-you-go token prices**.
- **Peak / off-peak pricing**: For time-of-day priced models like DeepSeek, it separately lists **peak / off-peak / cache-hit** prices so you can see the night-discount gap at a glance.
- **Offline fallback**: Ships with a 1.8MB price cache, so it **works even without internet**.
- **Zero dependencies**: Uses only the Python standard library — **no `pip install` required**.
- **Cross-platform**: Works on Windows / macOS / Linux with Python 3.8+.
- **Easy to extend**: Add or remove models by editing `watchlist.json`; change subscription / peak pricing by editing two JSON files.

---

## 📊 Data Sources

| Category | Source | Notes |
| --- | --- | --- |
| Token prices | [LiteLLM `model_prices_and_context_window.json`](https://github.com/BerriAI/litellm) | Community-maintained, covering OpenAI / Anthropic / Google / DeepSeek / Qwen / Kimi / GLM / Llama / Mistral and thousands more |
| Subscription / peak prices | Vendor official websites | Stored in local config files for easy correction |

---

## 📁 Project Structure

```
.
├── main.py                  # Entry point: python main.py = update + generate
├── fetch_prices.py          # Fetch / cache the LiteLLM dataset and normalize by watchlist
├── generate_md.py           # Merge subscription + token prices and render Markdown
├── watchlist.json           # The list of tracked models (add / remove freely)
├── subscription.json        # Subscription / plan prices (manually maintained)
├── pricing_overrides.json   # Peak / special pricing (manually maintained)
├── model_prices_cache.json  # Snapshot of the online dataset (offline fallback, auto-updated)
└── LLM价格汇总.md           # Final output (auto-generated)
```

---

## 🚀 Quick Start

### Requirements
Only **Python 3.8+** is needed — no third-party packages.

### Three steps

```bash
# 1. Clone this repository
git clone https://github.com/<your-username>/llm-price-summary.git
cd llm-price-summary

# 2. One-click update latest prices and generate the summary
python main.py          # on Windows it may be `py main.py`; on macOS/Linux `python3 main.py`

# 3. Open the generated LLM价格汇总.md to view
```

---

## 🛠 Usage

The tool provides three run modes (commands are identical across platforms):

```bash
python main.py            # update the online price cache + regenerate LLM价格汇总.md
python main.py --update   # only refresh the online price cache (no md regeneration)
python main.py --no-update# offline: generate md using the local cache only
```

The generated `LLM价格汇总.md` contains:

1. **Subscription / plan price table**: plans, monthly cost, and included quota, grouped by vendor.
2. **Token price table (API pay-as-you-go)**: grouped by vendor, normalized to "per 1M (million) tokens" for easy comparison; includes context window and cache-hit price. Models with peak/off-peak pricing (e.g. DeepSeek) get separate peak / off-peak columns.
3. **Usage notes**: the script auto-appends the three run commands.

### Add / remove tracked models
Edit `watchlist.json`. Each entry looks like:

```json
{
  "provider": "OpenAI",
  "display": "GPT-4o",
  "litellm_key": "gpt-4o"
}
```

- `provider`: vendor group name (decides which section it lands in the Markdown).
- `display`: the name shown in the table.
- `litellm_key`: the exact model key in the LiteLLM dataset (search `model_prices_cache.json` to confirm; note many keys carry a vendor prefix such as `anthropic.`, `dashscope/`, `deepinfra/meta-llama/`).

### Edit subscription / peak prices
- Subscription plans → edit `subscription.json`.
- Peak / special pricing (e.g. DeepSeek) → edit `pricing_overrides.json`; see the in-file example (`peak` / `offpeak` / `cache_hit_input` / `window` fields).

---

## ⏱ Peak / Off-peak Pricing (DeepSeek example)

In `pricing_overrides.json`, the DeepSeek series is maintained separately in official RMB pricing:

| Model | Peak Input | Peak Output | Off-peak Input | Off-peak Output | Cache-hit Input | Discount Window |
| --- | --- | --- | --- | --- | --- | --- |
| DeepSeek-V3 | ¥1 / 1M | ¥2 / 1M | ¥0.5 / 1M | ¥1 / 1M | ¥0.1 / 1M | 00:30–08:30 (Beijing) |
| DeepSeek-R1 | ¥4 / 1M | ¥16 / 1M | ¥1 / 1M | ¥4 / 1M | ¥1 / 1M | 00:30–08:30 (Beijing) |

When you add a model with peak/off-peak pricing, give that `watchlist.json` entry an `"override": "corresponding-key"` and maintain the matching fields in `pricing_overrides.json`.

---

## ⚠️ Data Reliability & Disclaimer

- Token prices are pulled automatically from the LiteLLM public dataset and follow its update cadence.
- A few models (e.g. ByteDance Doubao, Zhipu GLM-4-Plus) have **no reliable price fields** in the public dataset. To avoid showing fake data, they are only marked "see official site" in the subscription table. To fill them in, add RMB reference prices to `pricing_overrides.json` with an `override` field.
- Subscription prices are approximate values compiled from official sites (with rough ¥ conversion), for reference only.
- **Always refer to each vendor's official real-time pricing.** This repository is not responsible for any losses caused by price discrepancies.

---

## 🔧 Advanced: Double-click Launchers (optional)

Prefer not to type commands? Create your own launcher:

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
Then make it executable: `chmod +x 更新价格.command`.

---

## 📄 License

Released under the [MIT License](./LICENSE).
