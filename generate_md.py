"""将订阅价 + Token 价渲染为 Markdown 汇总文件。"""
import datetime
import json
import os

from fetch_prices import per_million, resolve

BASE = os.path.dirname(os.path.abspath(__file__))


def fmt_money(v, cur="$"):
    if v is None:
        return "—"
    return f"{cur}{v:g}"


def human_ctx(v):
    if not isinstance(v, (int, float)):
        return "—"
    if v >= 1_000_000:
        return f"{v / 1_000_000:.2f}M"
    if v >= 1000:
        return f"{v / 1000:.0f}K"
    return str(v)


def run(data):
    wl = json.load(open(os.path.join(BASE, "watchlist.json"), encoding="utf-8"))
    ov = json.load(open(os.path.join(BASE, "pricing_overrides.json"), encoding="utf-8"))
    sub = json.load(open(os.path.join(BASE, "subscription.json"), encoding="utf-8"))

    groups = {}
    not_found = []
    for e in wl:
        key, m = resolve(e, data)
        if key is None:
            not_found.append(e["display"])
            continue
        prov = e["provider"]
        ovk = e.get("override")
        override = ov.get(ovk, {}) if ovk else {}
        ctx = m.get("max_input_tokens") or m.get("max_tokens")
        row = {"display": e["display"], "context": ctx}
        if override and "peak" in override and "offpeak" in override:
            cur = override.get("currency", "¥")
            row["type"] = "peak"
            row["cur"] = cur
            row["peak_in"] = override["peak"].get("input_miss")
            row["peak_out"] = override["peak"].get("output")
            row["off_in"] = override["offpeak"].get("input_miss")
            row["off_out"] = override["offpeak"].get("output")
            row["cache_in"] = override["peak"].get("cache_hit_input")
            row["window"] = override["offpeak"].get("window", "")
            row["note"] = override.get("note", "")
        else:
            row["type"] = "std"
            row["cur"] = "$"
            row["in"] = per_million(m.get("input_cost_per_token"))
            row["out"] = per_million(m.get("output_cost_per_token"))
            row["cache_in"] = per_million(m.get("cache_read_input_token_cost"))
            row["note"] = override.get("note", "") if override else ""
        groups.setdefault(prov, []).append(row)

    L = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    L.append("# 大语言模型（LLM）价格汇总\n")
    L.append(f"> 更新时间：**{now}（本地时间）**  ")
    L.append("> 数据来源：Token 价格来自社区维护的公开数据集 [LiteLLM model_prices](https://github.com/BerriAI/litellm)；订阅 / 峰谷价格由各厂商官网整理。  ")
    L.append("> ⚠️ 本表为公开整理，**仅供参考，请以各厂商官网实时报价为准**。\n")

    L.append("## 一、订阅 / 套餐价格\n")
    L.append("| 厂商 | 套餐 | 价格 | 包含 / 额度 | 备注 |")
    L.append("| --- | --- | --- | --- | --- |")
    for s in sub:
        L.append(
            f"| {s.get('provider','')} | {s.get('plan','')} | {s.get('price','')} "
            f"| {s.get('included','')} | {s.get('note','')} |"
        )
    L.append("")

    L.append("## 二、Token 价格（API 按量）\n")
    L.append("> 价格统一换算为「每百万 (1M) tokens」计价，便于横向对比。\n")
    for prov, rows in groups.items():
        L.append(f"### {prov}\n")
        has_peak = any(r["type"] == "peak" for r in rows)
        if has_peak:
            L.append(
                "| 模型 | 峰时输入 | 峰时输出 | 谷时输入 | 谷时输出 "
                "| 缓存命中输入 | 上下文 | 优惠时段 | 备注 |"
            )
            L.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
            for r in rows:
                if r["type"] == "peak":
                    L.append(
                        f"| {r['display']} | {fmt_money(r['peak_in'], r['cur'])} "
                        f"| {fmt_money(r['peak_out'], r['cur'])} | {fmt_money(r['off_in'], r['cur'])} "
                        f"| {fmt_money(r['off_out'], r['cur'])} | {fmt_money(r['cache_in'], r['cur'])} "
                        f"| {human_ctx(r['context'])} | {r.get('window','')} | {r.get('note','')} |"
                    )
                else:
                    L.append(
                        f"| {r['display']} | {fmt_money(r['in'], r['cur'])} "
                        f"| {fmt_money(r['out'], r['cur'])} | — | — "
                        f"| {fmt_money(r['cache_in'], r['cur'])} | {human_ctx(r['context'])} "
                        f"| — | {r.get('note','')} |"
                    )
        else:
            L.append("| 模型 | 输入 | 输出 | 缓存命中输入 | 上下文 | 备注 |")
            L.append("| --- | --- | --- | --- | --- | --- |")
            for r in rows:
                L.append(
                    f"| {r['display']} | {fmt_money(r['in'], r['cur'])} "
                    f"| {fmt_money(r['out'], r['cur'])} | {fmt_money(r['cache_in'], r['cur'])} "
                    f"| {human_ctx(r['context'])} | {r.get('note','')} |"
                )
        L.append("")

    if not_found:
        L.append("### 备注：以下模型本次未匹配到在线价格（可检查 watchlist.json 的 key）\n")
        L.append("- " + "、".join(not_found) + "\n")

    L.append("## 三、如何使用\n")
    L.append("- **一键更新最新价格**：运行 `python main.py`（自动拉取最新 Token 价格并重新生成本文件）。")
    L.append("- **仅更新缓存**：`python main.py --update`")
    L.append("- **仅用本地缓存生成**（无网时）：`python main.py --no-update`")
    L.append("- **增删模型**：编辑 `watchlist.json`（添加厂商与模型 key）。")
    L.append("- **修改订阅价 / 峰谷价**：编辑 `subscription.json` 与 `pricing_overrides.json`。\n")

    out = os.path.join(BASE, "LLM价格汇总.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    return out
