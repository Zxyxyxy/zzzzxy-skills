"""Render a completed mock interview as standalone HTML and Markdown (Python 3.9+)."""
import argparse
import base64
import hashlib
import html
import json
from pathlib import Path
import re
from privacy import redact

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
KINDS = {'good': '亮点', 'gap': '待补', 'tip': '建议'}
ROLES = {'interviewer': '面试官', 'candidate': '候选人', 'coach': '提示'}


def clean(value, names):
    if isinstance(value, str):
        return redact(value, names)
    if isinstance(value, list):
        return [clean(item, names) for item in value]
    if isinstance(value, dict):
        return {key: clean(item, names) for key, item in value.items()}
    return value


def require_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} 必须为非空文本')


def text_list(value, field, allow_empty=True):
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ValueError(f'{field} 必须为文本数组' + ('且不为空' if not allow_empty else ''))
    for item in value:
        require_text(item, field)


def validate(data):
    if not isinstance(data, dict):
        raise ValueError('输入必须为 JSON 对象')
    if data.get('mode') not in ('practice', 'demo'):
        raise ValueError('mode 必须为 practice 或 demo')
    for field in ('summary', 'next_steps'):
        text_list(data.get(field), field, allow_empty=False)
    text_list(data.get('settings', []), 'settings')
    require_text(data.get('title', '模拟面试报告'), 'title')
    if not isinstance(data.get('sections'), list):
        raise ValueError('sections 必须为数组')
    sections, turns = set(), {}
    for section in data['sections']:
        if not isinstance(section, dict):
            raise ValueError('section 必须为对象')
        require_text(section.get('id'), 'section.id')
        require_text(section.get('title'), 'section.title')
        if section['id'] in sections:
            raise ValueError('阶段 id 重复')
        sections.add(section['id'])
        text_list(section.get('context', []), 'context')
        if 'status' in section:
            require_text(section['status'], 'status')
        if not isinstance(section.get('turns'), list):
            raise ValueError('turns 必须为数组')
        for turn in section['turns']:
            if not isinstance(turn, dict):
                raise ValueError('turn 必须为对象')
            require_text(turn.get('id'), 'turn.id')
            require_text(turn.get('text'), 'turn.text')
            if turn['id'] in turns:
                raise ValueError('问答 id 重复')
            if turn.get('role') not in ROLES or not isinstance(turn.get('assisted', False), bool):
                raise ValueError('角色或 assisted 类型不正确')
            if turn.get('assisted') and turn['role'] != 'candidate':
                raise ValueError('assisted 仅适用于候选人回答')
            turns[turn['id']] = turn
    annotations = data.get('annotations', [])
    if not isinstance(annotations, list):
        raise ValueError('annotations 必须为数组')
    spans = {}
    for index, note in enumerate(annotations, 1):
        if not isinstance(note, dict):
            raise ValueError('批注必须为对象')
        require_text(note.get('turn'), 'annotation.turn')
        require_text(note.get('quote'), 'annotation.quote')
        require_text(note.get('note'), 'annotation.note')
        if note.get('kind') not in KINDS or note['turn'] not in turns:
            raise ValueError('批注类型错误或对应问答不存在')
        text, quote = turns[note['turn']]['text'], note['quote']
        if text.count(quote) != 1 or '\n' in quote:
            raise ValueError(f'第 {index} 条批注必须唯一命中同一段原句')
        start = text.index(quote)
        end = start + len(quote)
        if any(start < b and end > a for a, b, _, _ in spans.get(note['turn'], [])):
            raise ValueError('同一轮批注不能重叠')
        spans.setdefault(note['turn'], []).append((start, end, index, note))
    return turns, spans


def paragraphs(text):
    return ''.join(f'<p>{p}</p>' for p in re.split(r'\n\s*\n', text) if p.strip())


def role_label(turn):
    return ROLES[turn['role']] + (' · 提示后练习' if turn.get('assisted') else '')


def turn_html(turn, spans):
    text, out, last = turn['text'], [], 0
    for start, end, index, note in sorted(spans.get(turn['id'], [])):
        out.append(html.escape(text[last:start]))
        tooltip = html.escape(f'{KINDS[note["kind"]]}：{note["note"]}', quote=True)
        out.append(f'<mark class="note-{note["kind"]}" aria-describedby="note-{index}" title="{tooltip}">{html.escape(text[start:end])}</mark>')
        last = end
    out.append(html.escape(text[last:]))
    assisted = ' assisted' if turn.get('assisted') else ''
    return f'<div class="turn {turn["role"]}{assisted}"><div class="role">{html.escape(role_label(turn))} <span>{html.escape(turn["id"])}</span></div><div class="turn-text">{paragraphs("".join(out))}</div></div>'


def notes_html(section, spans):
    notes = []
    for turn in section['turns']:
        for _, _, index, note in sorted(spans.get(turn['id'], [])):
            notes.append(f'<div class="annotation note-{note["kind"]}" id="note-{index}"><span class="annotation-label">{KINDS[note["kind"]]}</span><div><span class="note-source">{html.escape(turn["id"])}</span><q>{html.escape(note["quote"])}</q><p>{html.escape(note["note"])}</p></div></div>')
    return '<aside class="annotations" aria-label="本节批注">' + ''.join(notes) + '</aside>' if notes else ''


def paragraph_list(items):
    return ''.join(paragraphs(html.escape(item)) for item in items)


def build(data):
    _, spans = validate(data)
    legend = '<div class="legend" aria-label="批注颜色"><span class="note-good">亮点</span><span class="note-gap">待补</span><span class="note-tip">建议</span></div>'
    overview = paragraph_list(data['summary'])
    if data.get('settings'):
        overview += '<details class="question"><summary><h3>本轮范围</h3><span class="chevron" aria-hidden="true"></span></summary><div class="answer">' + paragraph_list(data['settings']) + '</div></details>'
    groups = [('本场模拟面试总结报告', overview)]
    for section in data['sections']:
        content = paragraph_list(section.get('context', []))
        if section.get('status'):
            content += '<p class="section-status">' + html.escape(section['status']) + '</p>'
        if section['turns']:
            content += '<details class="question" open><summary><h3>完整问答</h3><span class="chevron" aria-hidden="true"></span></summary><div class="answer">'
            content += ''.join(turn_html(t, spans) for t in section['turns']) + '</div></details>'
        content += notes_html(section, spans)
        groups.append((section['title'], content))
    groups.append(('下一轮练习', '<ol>' + ''.join('<li>' + html.escape(s) + '</li>' for s in data['next_steps']) + '</ol>'))
    nav, panels = [], []
    for i, (heading, content) in enumerate(groups):
        initial = ' data-initial' if i == 0 else ''
        nav.append(f'<a class="nav-link" href="#panel-{i}" data-panel="panel-{i}"{initial}>{html.escape(heading)}</a>')
        button = '<button class="expand-button" data-expand>展开本组全部</button>' if '<details' in content else ''
        panels.append(f'<article class="panel" id="panel-{i}"><div class="panel-heading"><h2 tabindex="-1">{html.escape(heading)}</h2>{button}</div><div class="panel-content">{content}</div></article>')
    css = (ASSETS / 'report.css').read_text(encoding='utf-8') + '\n' + (ASSETS / 'mock-interview.css').read_text(encoding='utf-8')
    js = (ASSETS / 'report.js').read_text(encoding='utf-8')
    digest = base64.b64encode(hashlib.sha256(js.encode()).digest()).decode()
    csp = f"default-src 'none'; script-src 'sha256-{digest}'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; connect-src 'none'"
    title = html.escape(data.get('title', '模拟面试报告'))
    mode = '<span class="mode-badge">AI 自问自答演示</span>' if data['mode'] == 'demo' else ''
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="{csp}"><title>{title}</title><style>{css}</style></head><body>
<a class="skip-link" href="#reader">跳转到正文</a><header class="topbar"><div class="topbar-inner"><div class="title-group"><div><h1>{title}</h1>{mode}{legend}</div></div><div class="top-actions"><button id="print">打印 / 保存 PDF</button><button id="mode" class="mode-button" aria-pressed="false">阅读全文</button></div></div></header>
<div class="workspace"><aside class="sidebar"><nav class="nav-list" aria-label="阅读目录">{''.join(nav)}</nav></aside><main class="reader" id="reader"><div class="reader-status"><span id="chapter-label">按模块阅读</span></div>{''.join(panels)}<div class="reader-footer"><button id="previous">上一模块</button><span id="position" aria-live="polite"></span><button id="next">下一模块</button></div></main></div><script>{js}</script></body></html>'''


def markdown(data):
    out = ['# ' + data.get('title', '模拟面试报告'), 'AI 自问自答演示' if data['mode'] == 'demo' else '用户模拟面试记录', '## 本场模拟面试总结报告', *data['summary']]
    if data.get('settings'):
        out += ['### 本轮范围', *data['settings']]
    for section in data['sections']:
        out += ['## ' + section['title'], *section.get('context', [])]
        if section.get('status'):
            out.append(section['status'])
        for turn in section['turns']:
            out += [f'### {turn["id"]}｜{role_label(turn)}', turn['text']]
        for note in data.get('annotations', []):
            if note['turn'] in {t['id'] for t in section['turns']}:
                out += [f'**{KINDS[note["kind"]]} · {note["turn"]}**', f'原句：{note["quote"]}', note['note']]
    out += ['## 下一轮练习', *[f'{i}. {s}' for i, s in enumerate(data['next_steps'], 1)]]
    return '\n\n'.join(out) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--redact', action='append', default=[], help='Exact identity string to mask; may be repeated')
    args = parser.parse_args()
    md_path = args.output.with_suffix('.md')
    if args.output.suffix.lower() != '.html' or args.input.resolve() in {args.output.resolve(), md_path.resolve()}:
        parser.error('输出需为 .html，且不能覆盖输入文件')
    try:
        raw = json.loads(args.input.read_text(encoding='utf-8'))
        validate(raw)
        data = clean(raw, args.redact)
        document = build(data)
        md = markdown(data)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document, encoding='utf-8')
    md_path.write_text(md, encoding='utf-8')
    print(args.output.resolve())
    print(md_path.resolve())


if __name__ == '__main__':
    main()
