"""overall 的分数与结论 —— 由逐条状态算出，不让模型自己编。

为什么不让模型给分：
    模型很擅长判「这条满足吗」，很不擅长给一个跨样本可比的 0-100 分。
    同一份简历问两次能差 15 分，而且分数和它自己的逐条判定经常矛盾
    （逐条全 matched，总分给 72）。一个看起来权威、实际不可比的数字，
    比没有数字更糟——用户会拿它做决定。

    所以：模型只负责逐条判定（它的强项），分数由规则从状态算出（确定、可复现、
    可解释、改权重不用重跑模型）。
"""

# 各状态的得分权重
_W_MATCHED = 1.0
_W_UNKNOWN = 0.5    # 判断不了不算错，给一半——避免简历写得简略被过度惩罚
_W_GAP = 0.0

# gap 严重度的额外扣分（占总分百分点）
_PENALTY = {"blocking": 18, "major": 6, "minor": 0}


def derive(requirements):
    """requirements: [{requirement, status, severity?}] → {score, verdict}"""
    if not requirements:
        return {"score": 0, "verdict": "mismatch"}

    total = 0.0
    for r in requirements:
        st = r.get("status")
        if st == "matched":
            total += _W_MATCHED
        elif st == "unknown":
            total += _W_UNKNOWN
        else:
            total += _W_GAP
    base = total / len(requirements) * 100

    penalty = sum(
        _PENALTY.get(r.get("severity") or "", 0)
        for r in requirements
        if r.get("status") == "gap"
    )
    score = max(0, min(100, round(base - penalty)))

    blocking = sum(
        1 for r in requirements
        if r.get("status") == "gap" and r.get("severity") == "blocking"
    )

    # 硬门槛优先于分数：两个以上硬性不满足，分数再高也是 mismatch
    if blocking >= 2:
        verdict = "mismatch"
    elif blocking == 1:
        verdict = "stretch"
    elif score >= 85:
        verdict = "strong"
    elif score >= 65:
        verdict = "fit"
    elif score >= 40:
        verdict = "stretch"
    else:
        verdict = "mismatch"

    return {"score": score, "verdict": verdict}
