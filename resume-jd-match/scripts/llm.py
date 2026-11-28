"""百炼 Qwen 客户端 —— 只用标准库，不装 SDK。

走百炼的 OpenAI 兼容接口，但**不用 openai 这个包**：
  - 省掉一个依赖（WhatAJob 那边也是零依赖风格，系统 python 3.9 装包容易出事）
  - 请求体就是 OpenAI 那套 JSON，换供应商改 BASE_URL + MODEL 两行即可

百炼的两个坑（已处理）：
  1. response_format={"type":"json_object"} 时，messages 里**必须出现 "json"
     这个词**，否则服务端 400 直接拒。见 _ensure_json_hint。
  2. 兼容接口只接受 json_object，**不支持 json_schema**。所以 schema 只能写在
     prompt 里靠模型遵循，校验必须自己做（validate.py）。这不是可选项。
"""
import json
import os
import time
import urllib.error
import urllib.request

BASE_URL = os.environ.get(
    "QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
)
MODEL = os.environ.get("QWEN_MODEL", "qwen-plus")
_TIMEOUT = 120


class LLMError(RuntimeError):
    pass


def _api_key():
    k = os.environ.get("DASHSCOPE_API_KEY")
    if not k:
        raise LLMError("没有 DASHSCOPE_API_KEY。请在当前进程环境中设置；配置示例见 scripts/env-example.txt。")
    return k


def _ensure_json_hint(messages):
    """百炼要求：用 json_object 时 messages 必须含 'json' 字面词，否则 400。"""
    joined = " ".join(m.get("content") or "" for m in messages)
    if "json" in joined.lower():
        return messages
    out = list(messages)
    out[-1] = dict(out[-1])
    out[-1]["content"] = (out[-1].get("content") or "") + "\n\n只输出 JSON。"
    return out


def chat_json(system, user, model=None, temperature=0, retries=2):
    """调模型并解析 JSON。失败重试，最后仍失败则抛 LLMError。

    返回 (data, meta)；meta 含 token 用量和耗时，用于成本核算。
    """
    messages = _ensure_json_hint([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])
    payload = {
        "model": model or MODEL,
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL.rstrip("/") + "/chat/completions",
        data=body,
        headers={
            "Authorization": "Bearer " + _api_key(),
            "Content-Type": "application/json",
        },
        method="POST",
    )

    last = None
    for attempt in range(retries + 1):
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
            content = raw["choices"][0]["message"]["content"]
            data = json.loads(content)
            usage = raw.get("usage") or {}
            return data, {
                "elapsed": round(time.time() - t0, 2),
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "model": payload["model"],
                "attempt": attempt + 1,
            }
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "ignore")[:400]
            last = LLMError("HTTP %s: %s" % (e.code, detail))
            # 4xx 是请求本身的问题（key 错、模型名错、参数错），重试没用
            if 400 <= e.code < 500 and e.code != 429:
                raise last
        except json.JSONDecodeError as e:
            last = LLMError("返回的不是合法 JSON: %s" % e)
        except Exception as e:  # 网络抖动等
            last = LLMError("%s: %s" % (type(e).__name__, e))
        if attempt < retries:
            time.sleep(1.5 * (attempt + 1))
    raise last
