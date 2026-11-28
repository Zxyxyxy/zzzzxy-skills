"""连通性自检 —— 只调一次模型，几乎不花钱。

先跑这个，确认 key / 网络 / 模型名都对了，再跑 run_eval.py。
不然 key 有问题的话会连着报 6 次一样的错。

用法:
    python3 check_key.py
"""
import os
import sys


def main():
    key = os.environ.get("DASHSCOPE_API_KEY")
    print("1) 检查 key …", end=" ")
    if not key:
        print("✗ 没读到")
        print()
        print("   环境变量 DASHSCOPE_API_KEY 是空的。在这个终端里跑：")
        print("     export DASHSCOPE_API_KEY=sk-你的key")
        print("   然后再跑一次 python3 check_key.py")
        return 1
    if not key.startswith("sk-"):
        print("✗ 格式不对")
        print("   百炼的 key 一般以 sk- 开头，请检查所用平台与配置。")
        print("   （别把别的平台的 key 填进来了）")
        return 1
    print("✓ 已配置（不显示密钥）")

    import llm
    print("2) endpoint  : 已从配置加载")
    print("3) 模型      : 已从配置加载")
    print("4) 调一次…", end=" ", flush=True)

    try:
        data, meta = llm.chat_json(
            "你是一个测试器。只输出 JSON。",
            '返回这个 JSON，不要多加字段：{"ok": true}',
        )
    except Exception as e:
        print("✗ 失败")
        print()
        msg = str(e).replace(key, "[REDACTED]")
        print("   请求失败；请根据下方分类检查配置。")
        print()
        # 常见错误的人话解释
        if "401" in msg or "InvalidApiKey" in msg or "Incorrect API key" in msg:
            print("   → 这个 key 百炼不认。三种常见原因，按可能性排：")
            print()
            print("     a) 密钥所属平台与当前接口不匹配。")
            print("     b) 地域不匹配。各地域 key 不通用，北京的 key 不能配")
            print("        新加坡的域名（看上面第 2 行的 endpoint）。")
            print("     c) key 已失效或被删。")
            print()
            print("     正确的拿法：aliyun.com 登录 → 搜「百炼」进控制台")
            print("     → 右上角头像 → API-KEY → 创建我的 API-KEY")
        elif "Model not exist" in msg or "model" in msg.lower() and "not" in msg.lower():
            print("   → 模型名不对，或你的账号还没开通 qwen-plus。")
            print("     去控制台看「模型广场」里可用的模型名，然后：")
            print("       export QWEN_MODEL=实际可用的模型名")
        elif "Arrearage" in msg or "quota" in msg.lower() or "balance" in msg.lower():
            print("   → 欠费或额度用完了。去百炼控制台充值/看免费额度。")
        elif "Throttling" in msg or "429" in msg:
            print("   → 被限流了，等一分钟再试。")
        elif "must contain the word" in msg:
            print("   → 这是百炼的 json 关键词校验，理论上 llm.py 已处理，")
            print("     如果还报说明它改规则了，把这段报错发给我。")
        else:
            print("   → 不认识这个错误，把上面整段发给我。")
        return 1

    print("✓ 通了")
    print()
    print("   返回      : 已收到 JSON 响应")
    print("   耗时      : %ss" % meta.get("elapsed"))
    print("   token     : %s in / %s out"
          % (meta.get("prompt_tokens"), meta.get("completion_tokens")))
    print()
    print("一切正常。现在可以跑真的了：")
    print("  python3 run_eval.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
