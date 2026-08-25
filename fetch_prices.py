"""价格抓取与本地缓存模块。

数据来源：社区维护的公开数据集 LiteLLM model_prices_and_context_window.json
（覆盖 OpenAI / Anthropic / Google / DeepSeek / 通义 / 豆包 / Kimi / GLM / Llama / Mistral 等）。
"""
import json
import os
import urllib.request

REPO_URL = "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"
BASE = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE, "model_prices_cache.json")


def per_million(v):
    """单个 token 的价格 -> 每百万 token 价格。"""
    if isinstance(v, (int, float)):
        return round(v * 1_000_000, 4)
    return None


def resolve(entry, data):
    """按 litellm_key 精确匹配；否则按 prefix 模糊匹配（取字典序最大，近似最新）。"""
    key = entry.get("litellm_key")
    if key and key in data:
        return key, data[key]
    prefix = entry.get("prefix")
    if prefix:
        matches = [k for k in data if k.startswith(prefix)]
        if matches:
            k = sorted(matches)[-1]
            return k, data[k]
    return None, None


def update_cache():
    """拉取最新数据并写入缓存；失败则回退到已有缓存。返回 (data, 是否在线更新成功)。"""
    try:
        req = urllib.request.Request(
            REPO_URL, headers={"User-Agent": "llm-price-tool/1.0"}
        )
        with urllib.request.urlopen(req, timeout=40) as r:
            data = json.loads(r.read().decode("utf-8"))
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        return data, True
    except Exception as e:  # noqa: BLE001
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, encoding="utf-8") as f:
                return json.load(f), False
        raise RuntimeError("无法获取在线价格数据，且无本地缓存可用：" + str(e))


def load_cache():
    """加载本地缓存；不存在则尝试更新。"""
    if not os.path.exists(CACHE_FILE):
        return update_cache()
    with open(CACHE_FILE, encoding="utf-8") as f:
        return json.load(f), True
