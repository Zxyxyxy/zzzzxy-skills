"""Conservative local redaction helper; manually review shareable output."""
import re

def redact(text, known_names=()):
    """Conservative identifier masking; not a general-purpose name recognizer."""
    text = str(text or '')
    names = set(known_names)
    for match in re.finditer(r'(?:姓名|候选人姓名|Name)\s*[:：]\s*([^\n|｜,，;；<〔]{2,40})', text, re.I):
        value = match.group(1).strip()
        chinese = re.match(r'[\u4e00-\u9fff]{2,4}(?=$|\s)', value)
        if chinese:
            names.add(chinese.group())
        elif re.fullmatch(r'[A-Za-z]+(?:[ -][A-Za-z]+){1,3}', value):
            names.add(value)
    # Hide destinations and source filenames; retain descriptive link text.
    text = re.sub(r':codex-file-citation\{[^}]*\}', '【已上传资料】', text)
    text = re.sub(r'【用户上传的文件：[^】]*】', '【已上传资料】', text)
    def link_label(match):
        label = match[1]
        if re.search(r'\.(?:pdf|docx?|png|jpe?g)\b|/(?:Users|home|var)/|https?://', label, re.I):
            return '【参考资料】'
        return label + '〔链接已隐藏〕'
    text = re.sub(r'!?\[([^\]]*)\]\([^\n]*?\)', link_label, text)
    # A quoted path may contain spaces. For a bare path, prefer its known extension
    # so the following explanation is not accidentally removed with the path.
    path_start = r'(?:file://|/(?:Users|home|var)/|[A-Za-z]:\\)'
    text = re.sub(r'["`“]' + path_start + r'[^\n"`”]+["`”]', '【本地路径已隐藏】', text)
    text = re.sub(path_start + r'[^\n<>|｜，。；;]*?\.(?:pdf|docx?|md|html|png|jpe?g|zip)(?![A-Za-z0-9])', '【本地路径已隐藏】', text, flags=re.I)
    text = re.sub(path_start + r'[^\s<>|｜，。；;]+', '【本地路径已隐藏】', text)
    text = re.sub(r'https?://[^\s<>\]）]+', '【链接已隐藏】', text)
    text = re.sub(r'(?m)^([^\n]{0,160}\.(?:pdf|docx?|png|jpe?g))\s*$', '【来源文件已隐藏】', text, flags=re.I)
    text = re.sub(r'((?:来源文件|原始文件名|简历文件名)\s*[:：]\s*)[^\n|｜，。；;]+', r'\1【来源文件已隐藏】', text)
    text = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '〔邮箱已脱敏〕', text)
    text = re.sub(r'(?<!\d)\d{17}[\dXx](?!\d)', '〔身份证已脱敏〕', text)
    text = re.sub(r'(?<!\d)\d{16,19}(?!\d)', '〔账号已脱敏〕', text)
    text = re.sub(r'(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)', '〔电话已脱敏〕', text)
    text = re.sub(r'((?:电话|手机|联系电话|Phone|Tel|微信|WeChat)\s*[:：]\s*)[^\n|｜;；,，]+', r'\1〔联系方式已脱敏〕', text, flags=re.I)
    for name in sorted(names, key=len, reverse=True):
        if name and not name.startswith(('〔', '[')):
            text = text.replace(name, '〔候选人〕')
    return text
