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


def main():
    p = argparse.ArgumentParser(description="一键查询所有 LLM 价格")
    p.add_argument("--update", action="store_true", help="仅更新在线价格缓存")
    p.add_argument("--no-update", action="store_true", help="仅用本地缓存生成 Markdown")
    args = p.parse_args()

    if args.no_update:
        data, _ = fetch_prices.load_cache()
    else:
        data, ok = fetch_prices.update_cache()
        print("价格缓存更新：" + ("成功（在线）" if ok else "失败，已回退本地缓存"))

    out = generate_md.run(data)
    print("已生成：" + out)


if __name__ == "__main__":
    main()
