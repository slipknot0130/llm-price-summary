"""一键查询所有 LLM 价格 —— 入口。

用法：
    python main.py            # 更新缓存 + 生成 Markdown
    python main.py --update   # 仅更新在线价格缓存
    python main.py --no-update# 仅用本地缓存生成 Markdown（无网时用）
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fetch_prices
import generate_md
import generate_html


def main():
    p = argparse.ArgumentParser(description="一键查询所有 LLM 价格")
    p.add_argument("--update", action="store_true", help="仅更新在线价格缓存")
    p.add_argument("--no-update", action="store_true", help="仅用本地缓存生成 Markdown")
    args = p.parse_args()

    if args.no_update:
        data, _ = fetch_prices.load_cache()
        print("⚠️ 离线模式（--no-update）：使用本地缓存，价格可能不是最新的。")
    else:
        data, ok = fetch_prices.update_cache()
        if ok:
            print("✅ 已实时拉取最新在线价格（LiteLLM 公开数据集，共 "
                  + str(len(data)) + " 个模型）。")
        else:
            print("⚠️ 在线价格拉取失败，已回退到本地缓存（数据可能不是最新的）。"
                  "建议联网后重新运行 `python main.py`。")

    out_md = generate_md.run(data)
    print("已生成：" + out_md)
    out_html = generate_html.run(data)
    print("已生成：" + out_html)


if __name__ == "__main__":
    main()
