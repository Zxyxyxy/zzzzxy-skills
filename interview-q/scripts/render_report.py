"""Dependency-free, escaped HTML renderer for the interview-q Markdown contract."""
import argparse
import hashlib
import html
from pathlib import Path
import re

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
TRUNCATION_NOTICE = '本次内容被模型截断，请补全后再作为完整报告使用。'


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


def inline(text):
    value = html.escape(text)
    value = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', value)
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', value)


def prose(md):
    """Keep every non-empty source line; unknown Markdown remains readable text."""
    result, list_type = [], None
    for line in md.splitlines():
        stripped = line.strip()
        field = re.match(r'^[-*]\s+(\*\*[^*]*(?:依据|考察点|回答框架|可能追问|待补充信息)[^*]*\*\*.*)$', stripped)
        if field:
            stripped = line = field[1]
        match = re.match(r'^(?:[-*]\s+|(\d+)[.、]\s+)(.+)$', stripped)
        kind = ('ol' if match.group(1) else 'ul') if match else None
        if kind != list_type:
            if list_type:
                result.append(f'</{list_type}>')
            if kind:
                result.append(f'<{kind}>')
            list_type = kind
        if not stripped:
            continue
        if match:
            value = f' value="{int(match.group(1))}"' if match.group(1) else ''
            result.append(f'<li{value}>{inline(match.group(2))}</li>')
        elif stripped == '---':
            result.append('<hr>')
        else:
            cls = 'answer-label' if '回答框架' in stripped[:22] else 'follow-label' if any(x in stripped[:22] for x in ('可能追问', '待补充信息')) else 'evidence' if any(x in stripped[:25] for x in ('依据', '考察点')) else ''
            heading = re.match(r'^#{1,6}\s+(.+)$', stripped)
            if heading:
                result.append(f'<h4>{inline(heading[1])}</h4>')
            else:
                result.append(f'<p class="{cls}">{inline(line)}</p>')
    if list_type:
        result.append(f'</{list_type}>')
    return '\n'.join(result)


def sections(md):
    """Support the current ##/### contract and legacy ###/bold-question reports."""
    lines = md.replace('\r\n', '\n').split('\n')
    heading = re.compile(r'^(#{1,6})\s+(.+?)\s*$')
    matches = [heading.match(line) for line in lines]
    module_words = ('面试准备重点', '待核实点', '高概率', '情景题', '类别常见', '反问面试官', '优先准备', '脱敏与依据')
    levels = [len(m[1]) for m in matches if m and any(word in m[2] for word in module_words)]
    if not levels:
        levels = [len(m[1]) for m in matches if m and len(m[1]) >= 2]
    level = min(levels) if levels else 2
    result = []
    title, body, has_heading = '阅读说明', [], False
    for line, match in zip(lines, matches):
        if match and len(match[1]) == level:
            if has_heading or any(item.strip() for item in body):
                result.append((title, '\n'.join(body)))
            title, body = match[2], []
            has_heading = True
        else:
            body.append(line)
    if has_heading or any(item.strip() for item in body) or not result:
        result.append((title, '\n'.join(body)))
    return result, level


def question_parts(body, section_level, enabled):
    if not enabled:
        return body, []
    intro, questions, current = [], [], None
    for line in body.splitlines():
        heading = re.match(r'^#{' + str(section_level + 1) + r'}\s+(.+)$', line)
        legacy = re.match(r'^\*\*((?:题目\s*\d+|[QSC]\d+|[🔴🟡]?\s*P[012]｜).+?)\*\*\s*$', line)
        match = heading or legacy
        if match:
            current = [match[1], []]
            questions.append(current)
        elif current is not None:
            current[1].append(line)
        else:
            intro.append(line)
    return '\n'.join(intro), [(title, '\n'.join(lines)) for title, lines in questions]


def build(markdown, title='面试预判与追问', subtitle='面试准备报告', truncated=False):
    markdown = redact(markdown)
    groups, level = sections(markdown)
    nav, panels, question_count = [], [], 0
    for index, (heading, body) in enumerate(groups):
        panel_id = f'panel-{index}'
        enabled = any(word in heading for word in ('高概率', '情景题', '类别常见', '专业题'))
        intro, questions = question_parts(body, level, enabled)
        content = prose(intro)
        for number, (question, answer) in enumerate(questions, 1):
            priority = 'p0' if 'P0' in question else 'p1'
            content += f'<details class="question {priority}" id="{panel_id}-q{number}"><summary><h3>{inline(question)}</h3><span class="chevron" aria-hidden="true"></span></summary><div class="answer">{prose(answer)}</div></details>'
        question_count += len(questions)
        button = '<button type="button" class="expand-button" data-expand>展开本组全部</button>' if questions else ''
        panels.append(f'<article class="panel" id="{panel_id}" aria-labelledby="nav-{index}"><div class="panel-heading"><h2 tabindex="-1">{inline(heading)}</h2>{button}</div><div class="panel-content">{content}</div></article>')
        label = re.sub(r'^[^\w\u4e00-\u9fff]+\s*', '', heading)
        label = re.sub(r'^\d+[.、]\s*', '', label)
        label = re.sub(r'[（(](?:通常\s*)?\d+(?:[-–]\d+)?\s*题[）)]', '', label)
        count = f'<span class="nav-count">{len(questions)} 题</span>' if questions else ''
        initial = ' data-initial' if '面试准备重点' in heading else ''
        nav.append(f'<a href="#{panel_id}" id="nav-{index}" class="nav-link" data-panel="{panel_id}"{initial}><span>{inline(label)}</span>{count}</a>')
    title, subtitle = inline(redact(title)), inline(redact(subtitle))
    css = (ASSETS / 'report.css').read_text(encoding='utf-8')
    js = (ASSETS / 'report.js').read_text(encoding='utf-8')
    # Only our fixed code runs. Candidate/model content never reaches script or CSS.
    script_hash = __import__('base64').b64encode(hashlib.sha256(js.encode()).digest()).decode()
    csp = f"default-src 'none'; script-src 'sha256-{script_hash}'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; connect-src 'none'"
    warning = f'<p role="alert">{TRUNCATION_NOTICE}</p>' if truncated else ''
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="{csp}"><title>{title}</title><style>{css}</style></head><body>
<a class="skip-link" href="#reader">跳转到正文</a><header class="topbar"><div class="topbar-inner"><div class="title-group"><div class="page-mark" aria-hidden="true">面试<span>02</span></div><div><h1>{title}</h1><p class="subtitle">{subtitle}</p></div></div><div class="top-actions"><button type="button" id="print">打印 / 保存 PDF</button><button type="button" id="mode" class="mode-button" aria-pressed="false">阅读全文</button></div></div></header>
<div class="workspace"><aside class="sidebar"><p class="nav-caption">阅读目录</p><nav class="nav-list" aria-label="阅读目录">{''.join(nav)}</nav><p class="sidebar-note">按模块阅读，点击题目展开。<br>脱敏后的正文完整保留。</p></aside><main class="reader" id="reader"><div class="reader-status"><span id="chapter-label">按模块阅读</span><span class="status-hint">{question_count} 道题</span></div>{warning}{''.join(panels)}<div class="reader-footer"><button type="button" id="previous">上一模块</button><span id="position"></span><button type="button" id="next">下一模块</button></div></main></div><script>{js}</script></body></html>'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--title', default='面试预判与追问')
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error('输入和输出不能是同一文件')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(args.input.read_text(encoding='utf-8'), args.title), encoding='utf-8')
    print(args.output.resolve())
