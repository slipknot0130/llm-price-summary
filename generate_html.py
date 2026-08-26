"""将订阅价 + Token 价渲染为自包含、可离线打开的 HTML 页面。

特点：浅色主题、内嵌数据、纯 CSS 柱状对比图、分组表格，无需任何外部依赖或联网即可查看。
"""

import datetime
import json
import os

from fetch_prices import per_million, resolve

BASE = os.path.dirname(os.path.abspath(__file__))


def _load_settings():
    try:
        return json.load(open(os.path.join(BASE, "settings.json"), encoding="utf-8"))
    except Exception:
        return {}


SETTINGS = _load_settings()
RATE_USD_CNY = float(SETTINGS.get("usd_to_cny", 7.25))


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


def build_rows(data):
    wl = json.load(open(os.path.join(BASE, "watchlist.json"), encoding="utf-8"))
    ov = json.load(open(os.path.join(BASE, "pricing_overrides.json"), encoding="utf-8"))
    sub = json.load(open(os.path.join(BASE, "subscription.json"), encoding="utf-8"))

    groups = {}
    not_found = []
    chart_rows = []  # (label, value_per_1m, cur, is_peak_model)
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
            row["window"] = override.get("window", "")
            row["note"] = override.get("note", "")
            # 图表用峰时输出价代表该模型
            chart_rows.append((row["display"], override["peak"].get("output"), cur, True,
                               override["offpeak"].get("output")))
        else:
            row["type"] = "std"
            row["cur"] = "$"
            row["in"] = per_million(m.get("input_cost_per_token"))
            row["out"] = per_million(m.get("output_cost_per_token"))
            row["cache_in"] = per_million(m.get("cache_read_input_token_cost"))
            row["note"] = override.get("note", "") if override else ""
            chart_rows.append((row["display"], row["out"], "$", False, None))
        row["buy"] = e.get("buy_url", "")
        groups.setdefault(prov, []).append(row)
    return groups, sub, not_found, chart_rows


def _chart(chart_rows):
    # 把美元统一换算成人民币再画柱，避免 $ 与 ¥ 直接比数字产生的幻觉
    rate = RATE_USD_CNY

    def to_cny(v, cur):
        if not isinstance(v, (int, float)):
            return None, "—"
        if cur == "$":
            return v * rate, f"¥{v * rate:.2f}"
        return v, f"¥{v:g}"

    converted = []
    for label, value, cur, is_peak, off_val in chart_rows:
        cny_val, cny_text = to_cny(value, cur)
        off_cny_val, off_cny_text = to_cny(off_val, cur) if is_peak else (None, "—")
        converted.append((label, cny_val, cny_text, is_peak, off_val, cur, off_cny_val, off_cny_text))

    vals = [c[1] for c in converted if isinstance(c[1], (int, float))]
    if not vals:
        return ""
    mx = max(vals)
    if mx <= 0:
        mx = 1

    def bar(label, cny_val, cny_text, is_peak, off_val_orig, cur_orig, off_cny_val, off_cny_text):
        pct = (cny_val / mx * 100) if isinstance(cny_val, (int, float)) else 0
        fill = "#e74c3c" if is_peak else "#2563eb"
        val_text = "—" if not isinstance(cny_val, (int, float)) else cny_text
        extra = ""
        if is_peak and isinstance(off_cny_val, (int, float)):
            orig_off_text = (
                f"¥{off_val_orig:g}" if cur_orig == "¥" else f"${off_val_orig:g}"
            )
            extra = (
                f'<span class="peak-sub">峰 {val_text} · 谷 {off_cny_text}'
                f'<span style="color:#999">（原 {orig_off_text}）</span></span>'
            )
        elif is_peak:
            extra = f'<span class="peak-sub">峰 {val_text}</span>'
        return f'''
        <div class="bar-row">
          <div class="bar-label" title="{label}">{label}</div>
          <div class="bar-track">
            <div class="bar-fill" style="width:{pct:.1f}%;background:{fill}"></div>
          </div>
          <div class="bar-val">{val_text}</div>
        </div>{extra}'''

    rows_html = "".join(bar(*c) for c in converted)
    return f'''
    <div class="chart">
      <div class="chart-title">API 输出价对比（每百万 tokens，已统一换算为人民币）</div>
      <div class="chart-sub">柱长按人民币价格比例缩放 · 红=峰时计费　蓝=标准计费 · 汇率 1 USD ≈ ¥{rate:g}（可在 settings.json 中调整）</div>
      {rows_html}
    </div>'''


def run(data):
    groups, sub, not_found, chart_rows = build_rows(data)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    parts = []

    parts.append(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LLM 价格汇总</title>
<style>
  :root {{ color-scheme: light; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family: -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
         background:#f5f7fa; color:#1a1a1a; line-height:1.6; }}
  .wrap {{ max-width:980px; margin:0 auto; padding:28px 20px 60px; }}
  header {{ border-bottom:3px solid #2563eb; padding-bottom:16px; margin-bottom:24px; }}
  header h1 {{ margin:0 0 6px; font-size:26px; }}
  header .meta {{ color:#666; font-size:14px; }}
  .badge {{ display:inline-block; background:#fff3cd; color:#8a6d00; border:1px solid #ffe69c;
           padding:2px 10px; border-radius:999px; font-size:12px; margin-left:8px; }}
  .cards {{ display:flex; flex-wrap:wrap; gap:14px; margin:20px 0 28px; }}
  .card {{ background:#fff; border:1px solid #e6e8ec; border-radius:12px; padding:16px 18px; flex:1; min-width:150px; }}
  .card .num {{ font-size:24px; font-weight:700; color:#2563eb; }}
  .card .label {{ color:#888; font-size:13px; margin-top:4px; }}
  section {{ background:#fff; border:1px solid #e6e8ec; border-radius:12px; padding:20px; margin-bottom:22px; }}
  section h2 {{ margin:0 0 14px; font-size:18px; }}
  table {{ width:100%; border-collapse:collapse; font-size:14px; }}
  th,td {{ border:1px solid #e6e8ec; padding:8px 10px; text-align:left; }}
  th {{ background:#f0f4ff; color:#1a1a1a; }}
  tbody tr:nth-child(even) {{ background:#fafbfc; }}
  a.buy {{ display:inline-block; background:#2563eb; color:#fff; text-decoration:none;
          padding:5px 14px; border-radius:8px; font-size:13px; font-weight:600;
          border:1px solid #1d4ed8; box-shadow:0 1px 2px rgba(0,0,0,.12);
          transition: background .15s, transform .05s; }}
  a.buy:hover {{ background:#1d4ed8; }}
  a.buy:active {{ transform: translateY(1px); }}
  .note {{ color:#888; font-size:13px; }}
  .chart {{ background:#fff; border:1px solid #e6e8ec; border-radius:12px; padding:20px; }}
  .chart-title {{ font-weight:700; margin-bottom:4px; }}
  .chart-sub {{ color:#888; font-size:13px; margin-bottom:16px; }}
  .bar-row {{ display:flex; align-items:center; gap:10px; margin:6px 0; }}
  .bar-label {{ width:150px; flex:0 0 150px; font-size:13px; color:#333; white-space:nowrap;
               overflow:hidden; text-overflow:ellipsis; }}
  .bar-track {{ flex:1; background:#eef1f5; border-radius:6px; height:18px; overflow:hidden; }}
  .bar-fill {{ height:100%; border-radius:6px; }}
  .bar-val {{ width:90px; flex: 0 0 90px; text-align:right; font-size:13px; color:#333; }}
  .peak-sub {{ display:block; font-size:12px; color:#e74c3c; margin-left:160px; margin-top:-2px; }}
  footer {{ color:#999; font-size:13px; text-align:center; margin-top:30px; }}
  a {{ color:#2563eb; }}
  .warn {{ background:#fff4e5; border:1px solid #ffd9a0; color:#8a4b00; padding:10px 14px;
          border-radius:10px; margin-bottom:20px; font-size:14px; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>大语言模型（LLM）价格汇总 <span class="badge">默认实时拉取</span></h1>
    <div class="meta">更新时间：<b>{now}</b>（本地时间）　·　数据来源：
      <a href="https://github.com/BerriAI/litellm" target="_blank">LiteLLM 公开数据集</a>（Token 价）＋ 各厂商官网（订阅/峰谷）</div>
  </header>

  <div class="cards">
    <div class="card"><div class="num">{sum(len(v) for v in groups.values())}</div><div class="label">追踪模型数</div></div>
    <div class="card"><div class="num">{len(groups)}</div><div class="label">覆盖厂商</div></div>
    <div class="card"><div class="num">每百万</div><div class="label">统一计价单位</div></div>
    <div class="card"><div class="num">¥/$</div><div class="label">支持双币种</div></div>
  </div>

  <div class="warn">⚠️ 本页面为公开整理，<b>仅供参考，请以各厂商官网实时报价为准</b>。想拿到最新价，重跑 <code>python main.py</code> 即可实时更新。</div>

  <section>
    <h2>一、订阅 / 套餐价格</h2>""")

    # 按供应商分组（保序），每个供应商只展示一个购买按钮
    from collections import OrderedDict
    sub_grouped = OrderedDict()
    sub_provider_buy = OrderedDict()
    for s in sub:
        p = s.get("provider", "")
        if p not in sub_grouped:
            sub_grouped[p] = []
            sub_provider_buy[p] = ""
        sub_grouped[p].append(s)
        if s.get("buy_url") and not sub_provider_buy[p]:
            sub_provider_buy[p] = s["buy_url"]
    for prov, plans in sub_grouped.items():
        buy_html = (
            f' <a class="buy" href="{sub_provider_buy[prov]}" target="_blank">官网 ↗</a>'
            if sub_provider_buy.get(prov) else ""
        )
        parts.append(f"<h3>{prov}{buy_html}</h3>")
        parts.append(
            '<table><thead><tr><th>套餐</th><th>价格</th><th>包含 / 额度</th><th>备注</th></tr></thead><tbody>'
        )
        for s in plans:
            parts.append(
                f"<tr><td>{s.get('plan','')}</td>"
                f"<td>{s.get('price','')}</td>"
                f"<td>{s.get('included','')}</td>"
                f"<td class='note'>{s.get('note','')}</td></tr>"
            )
        parts.append("</tbody></table>")
    parts.append("</section>")

    parts.append('<section><h2>二、Token 价格（API 按量）</h2>'
                 '<p class="note">价格统一换算为「每百万 (1M) tokens」计价，便于横向对比；凡峰谷计费模型单独列出峰时 / 谷时。</p>')
    for prov, rows in groups.items():
        prov_buy = rows[0].get("buy", "") if rows else ""
        prov_btn = (
            f' <a class="buy" href="{prov_buy}" target="_blank">官网 ↗</a>'
            if prov_buy else ""
        )
        parts.append(f"<h3>{prov}{prov_btn}</h3>")
        has_peak = any(r["type"] == "peak" for r in rows)
        if has_peak:
            parts.append('<table><thead><tr><th>模型</th><th>峰时输入</th><th>峰时输出</th>'
                         '<th>谷时输入</th><th>谷时输出</th><th>缓存命中输入</th>'
                         '<th>上下文</th><th>优惠时段</th><th>备注</th></tr></thead><tbody>')
            for r in rows:
                if r["type"] == "peak":
                    parts.append(
                        f"<tr><td>{r['display']}</td>"
                        f"<td>{fmt_money(r['peak_in'], r['cur'])}</td>"
                        f"<td>{fmt_money(r['peak_out'], r['cur'])}</td>"
                        f"<td>{fmt_money(r['off_in'], r['cur'])}</td>"
                        f"<td>{fmt_money(r['off_out'], r['cur'])}</td>"
                        f"<td>{fmt_money(r['cache_in'], r['cur'])}</td>"
                        f"<td>{human_ctx(r['context'])}</td>"
                        f"<td class='note'>{r.get('window','')}</td>"
                        f"<td class='note'>{r.get('note','')}</td></tr>")
                else:
                    parts.append(
                        f"<tr><td>{r['display']}</td>"
                        f"<td>{fmt_money(r['in'], r['cur'])}</td>"
                        f"<td>{fmt_money(r['out'], r['cur'])}</td>"
                        f"<td>—</td><td>—</td>"
                        f"<td>{fmt_money(r['cache_in'], r['cur'])}</td>"
                        f"<td>{human_ctx(r['context'])}</td>"
                        f"<td>—</td>"
                        f"<td class='note'>{r.get('note','')}</td></tr>")
        else:
            parts.append('<table><thead><tr><th>模型</th><th>输入</th><th>输出</th>'
                         '<th>缓存命中输入</th><th>上下文</th><th>备注</th></tr></thead><tbody>')
            for r in rows:
                parts.append(
                    f"<tr><td>{r['display']}</td>"
                    f"<td>{fmt_money(r['in'], r['cur'])}</td>"
                    f"<td>{fmt_money(r['out'], r['cur'])}</td>"
                    f"<td>{fmt_money(r['cache_in'], r['cur'])}</td>"
                    f"<td>{human_ctx(r['context'])}</td>"
                    f"<td class='note'>{r.get('note','')}</td></tr>")
        parts.append("</tbody></table>")

    parts.append("</section>")

    parts.append(_chart(chart_rows))

    if not_found:
        parts.append('<section><h2>备注</h2><p class="note">以下模型本次未匹配到在线价格（可检查 watchlist.json 的 key）：'
                     + "、".join(not_found) + "</p></section>")

    parts.append(f'''<footer>
    <p>LLM 价格汇总 · 本地一键查询工具 · 开源 MIT License</p>
    <p>使用方式：<code>python main.py</code>（更新+生成） · <code>python main.py --update</code>（仅更新缓存） · <code>python main.py --no-update</code>（离线生成）</p>
  </footer>
</div>
</body>
</html>''')

    out = os.path.join(BASE, "llm-price.html")
    html = "".join(parts)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out
