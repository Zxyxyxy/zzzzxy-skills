"""JD 任职要求分条 —— 确定性，不用模型。

为什么必须确定性：
    skill 的核心不变量是「JD 有几条要求，输出就有几项」。如果条数由模型自己
    报，这个不变量是自证的、等于没有——模型把两条合并成一条、同时报 count=4，
    校验照样通过。所以条数必须在调模型**之前**算出来，作为外部真值注入。

分条规则按 jobs.db 里 44133 条真实 requirement 统计得出：
    43971 条（99.6%）用换行分条  → 换行为主
    22515 条含「1、」 13635 条含「1.」 → 数字前缀需剥离
    百度系用「-」开头，部分用「•」「·」
    59 条含「1)」 → 括号式极少，一并处理
"""
import re
import unicodedata

# 行首序号/项目符号：1、 1. 1) （1） - • · ● ▪ 等
_BULLET = re.compile(
    r"^\s*(?:"
    r"[（(]?\d{1,2}[)）.、，,:：]"   # 1、 1. 1) （1）
    r"|[-—–*•·●▪○◆·]+"              # - • · 等符号
    r"|[一二三四五六七八九十]{1,2}[、.)）]"  # 一、 二、
    r")\s*"
)

# 纯噪声行：只有标题、空白、或"任职要求"这类小标题
_NOISE = re.compile(
    r"^\s*$"
    r"|^[\s\-—=*#]+$"
    r"|^(任职要求|岗位要求|职位要求|我们希望你|你需要具备|Requirements?|Qualifications?)"
    r"[:：]?\s*$",
    re.IGNORECASE,
)


def split_requirements(raw):
    """把 requirement 原文切成一条条要求。

    返回 [str]，每条已剥离序号前缀和首尾标点，但**内容本身逐字保留**
    （evidence 校验和 prompt 里的 requirement 都依赖这个逐字性）。
    """
    if not raw:
        return []
    text = unicodedata.normalize("NFKC", str(raw))

    # 主路径：按换行切
    lines = [ln for ln in text.splitlines()]
    items = [ln for ln in lines if not _NOISE.match(ln)]

    # 回退：整段没换行（0.4% 的数据），按「数字序号」或「；」切
    if len(items) <= 1 and text.strip():
        body = items[0] if items else text
        # 优先按数字序号切，保留序号位置
        parts = re.split(r"(?=[（(]?\d{1,2}[)）.、])", body)
        parts = [p for p in parts if p.strip()]
        if len(parts) <= 1:
            parts = re.split(r"[；;]", body)
        items = [p for p in parts if not _NOISE.match(p)]

    out = []
    for it in items:
        s = _BULLET.sub("", it).strip()
        s = s.strip(" \t；;，,。.、")
        # 太短的不是一条要求（多半是切碎的残渣或小标题）
        if len(s) < 6:
            continue
        out.append(s)
    return out


def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
