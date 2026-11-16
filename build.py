"""원고(content/*.md) 한 벌로 교재 페이지와 강의 슬라이드를 함께 만든다.

    .venv/bin/python build.py        → dist/ 에 결과물 생성

원고 문법
  # 1장. 제목          장 (슬라이드: 장 표지)
  ## 1차시. 제목       차시 (슬라이드: 차시 구분)
  ### 제목             슬라이드 제목 (교재: 소제목)
  ---                  여기서 슬라이드를 강제로 나눔 (교재에는 안 보임)
  :::goal 제목 … :::   상자 — goal, try, note, error, summary, quiz,
                       answer(접히는 예시 답안), teacher(강사 메모 — 슬라이드에서는 빠짐)
  ```sql 캡션          코드 (sql, python, bash …)
  ```screen 캡션       터미널 화면 예시. 색칠하지 않고 글자 그대로
  ```result            실행 결과 (마크다운 표를 쓰면 표로, 아니면 글자 그대로)
  ```mermaid           도식 (erDiagram, flowchart …)
  ```stepper           SQL 실행 순서 따라가기 (JSON)
  ### 제목 {keep}      이 제목 아래는 자동으로 나누지 않고 한 슬라이드에 담음
  :::center … :::      안의 내용을 가운데 정렬
  :::cols … :::        안의 블록을 옆으로 나란히
  :::window 제목 … ::: 맥 창 모양 프레임(위에 DB 칩 + 제목)
  ```hub 캡션          가운데 DB와 양옆 팀. 한 줄에: 아이콘 | 이름 | left·center·right
  {{ic:database}}      글·HTML 안에 아이콘 하나
  ```icons 캡션        픽토그램 카드. 한 줄에 하나: 아이콘 | 제목 | 설명 | 색  (icons-lg 는 한 장 가득 큰 카드)
  ```flow 캡션         아이콘 흐름(→). 줄 사이에 + = → 한 줄을 넣으면 연결 기호가 바뀜
  ```compare 캡션      좌우 비교. 한 줄에: 아이콘 | 글 || 아이콘 | 글 (첫 줄은 머리글)
  **굵게**             초록 형광펜 밑줄 (강조)
  ==분홍==             분홍 형광펜 밑줄 (정말 중요한 것)
  ```bars 캡션         가로 막대그래프. series: A | B / unit: % / 그다음 줄마다 항목 | 값 | 값
  ```icons-def 캡션    큰 네모 아이콘 + 밑줄 제목 + '설명'·'예' 두 줄 카드 (줄 형식은 icons 와 같음)
  ```rows 캡션         아이콘이 붙은 표. 첫 줄 머리글, 한 줄에: 아이콘(~색) | 칸 | 칸 … → 키마다 한 줄씩. ?칸 은 그 칸만 따로
  ```erd 캡션          ERD 그림. 한 줄에: 엔터티 @아이콘 [*PK, 속성, 속성 (FK)] ; ||--o< 관계명 ; 엔터티
                       선: ||(1개) |<(1개 이상) o<(0개 이상) o|(0~1개), --는 실선(식별) ..는 점선(비식별)
  ```stats 캡션        숫자 타일. 한 줄에: 아이콘 | 숫자 | 이름
  {{erd:||--o<}}       글·표 안에 ERD 선 하나(A ── B)
  ```shot 캡션         화면 캡처. 안에 images/ 아래 파일 경로 한 줄. 비워 두면 '캡처 필요' 자리 표시
아이콘은 icons/ 폴더의 Lucide 아이콘 이름. 사람+엑셀처럼 user+file-spreadsheet 로 쓰면 작은 배지가 붙는다.
제품 로고는 si:postgresql 처럼 쓴다(icons/brands/, Simple Icons). 색 자리에 #4169E1 같은 브랜드 색을 쓴다.
icons 줄의 다섯째 칸은 카드 아래 '예:' 줄이 된다. [결과물] ERD 처럼 쓰면 '예' 대신 '결과물'.
색: rose · plum · lime · ivory · hot(분홍 강조) · warn(경고). 로고를 분홍 강조하려면 hot#4169E1. 생략하면 rose→plum→lime→ivory 순서로 돈다.
flow·compare 는 슬라이드에서 → 키를 누를 때마다 한 단계씩 나타난다.
"""
import html
import json
import math
import re
import shutil
from pathlib import Path

from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
DIST = ROOT / "dist"

md = MarkdownIt("commonmark", {"html": True, "breaks": True}).enable("table")  # 원고의 줄바꿈을 그대로 살린다
esc = html.escape

BOX_LABELS = {
    "goal": "학습 목표", "try": "직접 해 보기", "note": "참고",
    "error": "자주 하는 실수", "summary": "정리", "quiz": "확인 문제",
    "teacher": "강사 메모",   # 교재에만 나오고 슬라이드에는 안 나옴
    "answer": "예시 답안",    # 접혀 있다가 눌러서 펼침
}
SLIDE_BUDGET = 15  # 한 슬라이드에 담을 대략적인 줄 수. 넘치는 만큼은 slides.js 의 fit()이 글자를 줄여 맞춘다.
INTRO = 4          # 이 줄 수 이하의 도입 문단은 뒤따르는 코드·그림과 같은 슬라이드에 둔다.


# ---------------------------------------------------------------- 원고 읽기

def read_front_matter(text):
    meta = {}
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        text = text[m.end():]
    return meta, text


def parse_blocks(text):
    """마크다운을 큰 덩어리(블록) 목록으로 나눈다. 슬라이드 나누기의 단위가 된다."""
    lines = text.splitlines()
    blocks, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith("```"):
            info = line[3:].strip()
            lang, _, caption = info.partition(" ")
            body, i = [], i + 1
            while i < n and not lines[i].startswith("```"):
                body.append(lines[i]); i += 1
            blocks.append({"kind": "fence", "lang": lang, "caption": caption.strip(), "body": "\n".join(body)})
            i += 1
        elif line.startswith(":::"):
            kind, _, title = line[3:].strip().partition(" ")
            body, i, in_fence = [], i + 1, False
            while i < n and not (lines[i].strip() == ":::" and not in_fence):
                if lines[i].startswith("```"):
                    in_fence = not in_fence
                body.append(lines[i]); i += 1
            blocks.append({"kind": "box", "box": kind, "title": title.strip(), "body": "\n".join(body),
                           "children": parse_blocks("\n".join(body)) if kind != "quiz" else []})
            i += 1
        elif re.match(r"#{1,3} ", line):
            level = len(line) - len(line.lstrip("#"))
            text = line[level:].strip()
            keep = text.endswith("{keep}")
            blocks.append({"kind": "h", "level": level, "text": text[:-6].strip() if keep else text, "keep": keep})
            i += 1
        elif line.strip() == "---":
            blocks.append({"kind": "break"})
            i += 1
        else:
            body = []
            while i < n and lines[i].strip() and not re.match(r"(```|:::|#{1,3} |---\s*$)", lines[i]):
                body.append(lines[i]); i += 1
            blocks.append({"kind": "para", "text": "\n".join(body)})
    return blocks


def assign_ids(blocks):
    """제목마다 id를 붙인다: ch1, ch1-s1, ch1-s1-t1 … 교재와 슬라이드가 같은 id로 서로를 가리킨다."""
    c = [0, 0, 0]
    for b in blocks:
        if b["kind"] != "h":
            continue
        lv = b["level"]
        c[lv - 1] += 1
        for k in range(lv, 3):
            c[k] = 0
        b["id"] = "ch%d" % c[0] + ("-s%d" % c[1] if lv >= 2 else "") + ("-t%d" % c[2] if lv == 3 else "")


# ---------------------------------------------------------------- 블록 → HTML

def mark_pink(text):
    """==글자== → <mark>글자</mark>. `코드` 안은 건드리지 않는다."""
    codes = []   # 코드 조각은 잠시 자리표시로 바꿔 두어, ==…`코드`…== 처럼 강조 안에 코드가 있어도 묶이게 한다
    text = re.sub(r"`[^`]*`", lambda m: codes.append(m.group(0)) or "\x00%d\x00" % (len(codes) - 1), text)
    text = re.sub(r"==(?=\S)(.+?)(?<=\S)==", r"<mark>\1</mark>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def inline_icons(text):
    """{{ic:database}} → 글 안에 들어가는 아이콘. {{erd:||--o<}} → 글 안에 들어가는 ERD 선 하나."""
    text = re.sub(r"\{\{erd:([^}]+)\}\}", lambda m: erd_inline(m.group(1)), text)
    return re.sub(r"\{\{ic:([\w:-]+)\}\}", lambda m: '<span class="ic-inline">%s</span>' % icon_svg(m.group(1)), text)


def render_md(text):
    out = md.render(inline_icons(mark_pink(text)))
    # 마크다운이 만든 표(<table> 그대로)만 감싼다. 원고에 직접 쓴 <table class="…">는 건드리지 않는다.
    return re.sub(r"<table>.*?</table>", lambda m: '<div class="table-wrap">%s</div>' % m.group(0), out, flags=re.S)


def render_inline(text):
    return md.renderInline(inline_icons(mark_pink(text)))


# ---------------------------------------------------------------- 픽토그램 (icons · flow · compare)

ICONS = ROOT / "icons"
TONES = ["rose", "plum", "lime", "ivory"]


def icon_svg(name):
    brand = name.startswith("si:")                       # si:postgresql → icons/brands/ 의 Simple Icons 로고(채우기 방식)
    path = (ICONS / "brands" / ("%s.svg" % name[3:])) if brand else (ICONS / ("%s.svg" % name))
    if not path.exists():
        raise SystemExit("아이콘이 없습니다: %s" % path.relative_to(ROOT))
    svg = re.sub(r"<!--.*?-->|<title>.*?</title>", "", path.read_text(encoding="utf-8"), flags=re.S).strip()
    svg = re.sub(r"\s+", " ", svg).replace("> <", "><")  # 한 줄로: 원고 속 HTML 안에 넣어도 마크다운이 끊지 않게
    head, rest = svg.split(">", 1)                       # 크기·클래스는 바깥 <svg> 태그에서만 뺀다(안쪽 rect 크기는 그대로)
    head = re.sub(r'\s(class|width|height|role)="[^"]*"', "", head)
    extra = ' class="brand" fill="currentColor"' if brand else ""
    return head.replace("<svg", '<svg aria-hidden="true"' + extra, 1) + ">" + rest


def tone_attrs(tone, default):
    """색 이름이면 class, #RRGGBB 이면 브랜드 색(흰 동그라미 + 그 색 로고)."""
    if tone.startswith("#"):
        return "brand", "--brand:%s;" % tone
    if tone.startswith("hot#"):   # 브랜드 로고를 살린 채 분홍 강조 카드로
        return "hot tone-brand", "--brand:%s;" % tone[3:]
    return tone or default, ""


def bubble(spec):
    """'user+file-spreadsheet' → 사람 아이콘에 엑셀 배지."""
    main, _, badge = spec.strip().partition("+")
    extra = '<span class="picto-badge">%s</span>' % icon_svg(badge) if badge else ""
    return '<span class="picto-ic">%s%s</span>' % (icon_svg(main), extra)


def fields(line, n):
    f = [x.strip() for x in line.split("|")]
    return f + [""] * (n - len(f))


def caption(b):
    return '<figcaption>%s</figcaption>' % render_inline(b["caption"]) if b["caption"] else ""


def ex_label(ex, default="예"):
    """'[결과물] ERD' → ('결과물', 'ERD'). 대괄호가 없으면 '예'."""
    m = re.match(r"\[(.+?)\]\s*(.*)", ex)
    return (m.group(1), m.group(2)) if m else (default, ex)


def render_icons(b):
    rows = [l for l in b["body"].splitlines() if l.strip()]
    cards = []
    for i, line in enumerate(rows):
        ic, title, desc, tone, ex = fields(line, 5)
        cls, style = tone_attrs(tone, TONES[i % 4])
        if b["lang"] == "icons-def":   # 큰 네모 아이콘 + 밑줄 제목 + 설명·예 두 줄
            dl = "".join('<dt>%s</dt><dd>%s</dd>' % (k, render_inline(v)) for k, v in (("설명", desc), ex_label(ex)) if v)
            cards.append('<li class="def-card tone-%s" style="%s--i:%d"><span class="def-tile">%s</span><b>%s</b><dl>%s</dl></li>' % (
                cls, style, i, icon_svg(ic), render_inline(title), dl))
            continue
        lab, ex = ex_label(ex)
        cards.append('<li class="picto-card tone-%s" style="%s--i:%d">%s<b>%s</b>%s%s</li>' % (
            cls, style, i, bubble(ic), render_inline(title),
            '<span class="d">%s</span>' % render_inline(desc) if desc else "",
            '<span class="ex"><em>%s</em>%s</span>' % (lab, render_inline(ex)) if ex else ""))
    if b["lang"] == "icons-def":
        return '<figure class="defs"><ul class="def-grid" style="--n:%d">%s</ul>%s</figure>' % (len(rows), "".join(cards), caption(b))
    size = " picto-lg" if b["lang"] == "icons-lg" else (" picto-one" if len(rows) == 1 else "")
    return '<figure class="picto%s"><ul class="picto-grid" style="--n:%d">%s</ul>%s</figure>' % (size, len(rows), "".join(cards), caption(b))


def render_stats(b):
    """숫자 타일. 한 줄에: 아이콘 | 숫자 | 이름"""
    tiles = []
    for i, line in enumerate(l for l in b["body"].splitlines() if l.strip()):
        ic, num, label = fields(line, 3)
        tiles.append('<li class="stat" style="--i:%d">%s<b>%s</b><span>%s</span></li>' % (i, bubble(ic), esc(num), render_inline(label)))
    return '<figure class="stats"><ul>%s</ul>%s</figure>' % ("".join(tiles), caption(b))


def render_rows(b):
    """아이콘이 붙은 표. 첫 줄은 머리글. 한 줄에: 아이콘(~색) | 칸 | 칸 …
    → 키마다 한 줄씩 나타난다. 칸 앞에 ? 를 붙이면 그 칸만 따로(줄 순서대로) 나타난다."""
    lines = [inline_icons(l) for l in b["body"].splitlines() if l.strip()]
    head, body = fields(lines[0], 0), [fields(l, 0) for l in lines[1:]]
    has_ic = any(r[0] not in ("", "-") for r in body)
    per_cell = any(c.startswith("?") for r in body for c in r[1:])
    th = "".join("<th>%s</th>" % render_inline(c) for c in head[1:])
    trs, k = [], 0
    for r in body:
        ic, _, tone = r[0].partition("~")
        icon = '<td class="rows-ic tone-%s">%s</td>' % (tone or "lime", bubble(ic) if ic not in ("", "-") else "") if has_ic else ""
        tds = []
        for c in r[1:]:
            if c.startswith("?"):
                tds.append('<td><span class="frag" style="--i:%d">%s</span></td>' % (k, render_inline(c[1:].strip()))); k += 1
            else:
                tds.append("<td>%s</td>" % render_inline(c))
        if per_cell:
            trs.append("<tr>%s%s</tr>" % (icon, "".join(tds)))
        else:
            trs.append('<tr class="frag" style="--i:%d">%s%s</tr>' % (k, icon, "".join(tds))); k += 1
    return '<figure class="rows"><table><thead><tr>%s%s</tr></thead><tbody>%s</tbody></table>%s</figure>' % (
        "<th></th>" if has_ic else "", th, "".join(trs), caption(b))


# ---------------------------------------------------------------- ERD (IE 표기법 · 까마귀발)

def erd_marks(code, side, w, y):
    """선 한쪽 끝의 기호. code는 원고에 보이는 순서 그대로(왼쪽 끝: 엔터티 쪽부터, 오른쪽 끝: 엔터티 쪽이 마지막)."""
    chars = [c for c in code if c in "|oO<>"]
    if side == "r":
        chars = chars[::-1]
    out, d = [], 8
    X = (lambda v: v) if side == "l" else (lambda v: w - v)
    for c in chars:
        if c in "<>":
            out.append('<path d="M%g %g L%g %g M%g %g L%g %g M%g %g L%g %g"/>' % (X(18), y, X(0), y - 11, X(18), y, X(0), y + 11, X(18), y, X(0), y))
            d = 26
        elif c == "|":
            out.append('<path d="M%g %g V%g"/>' % (X(d), y - 10, y + 10)); d += 9
        else:
            out.append('<circle cx="%g" cy="%g" r="6" fill="var(--paper)"/>' % (X(d + 6), y)); d += 16
    return "".join(out)


def erd_line_svg(spec, w=200, h=32):
    """'||--o<' (실선, 식별 관계) · '||..o<' (점선, 비식별 관계) → 선 하나 SVG."""
    m = re.match(r"\s*([|oO<>]*)\s*(--|\.\.)\s*([|oO<>]+)", spec)
    if not m:
        raise SystemExit("ERD 선 표기를 읽을 수 없습니다: %s" % spec)
    y = h / 2
    dash = ' stroke-dasharray="7 6"' if m.group(2) == ".." else ""
    return ('<svg class="erd-svg" viewBox="0 0 %d %d" width="%d" height="%d" aria-hidden="true">'
            '<path class="erd-path" d="M0 %g H%d"%s/><g class="erd-mk">%s%s</g></svg>') % (
        w, h, w, h, y, w, dash, erd_marks(m.group(1), "l", w, y), erd_marks(m.group(3), "r", w, y))


def erd_inline(spec):
    return '<span class="erd-inline"><b>A</b>%s<b>B</b></span>' % erd_line_svg(spec, 120, 28)


def erd_label(text):
    """'part_no (품번)' → 이름 뒤 괄호는 작은 글씨의 한글명으로."""
    m = re.match(r"(.*?)\s*\(([^()]*)\)\s*$", text)
    if not m or not m.group(1):
        return render_inline(text)
    return '%s<small class="erd-kr">%s</small>' % (render_inline(m.group(1)), render_inline(m.group(2)))


def erd_entity(spec, known, i):
    """'회원 @user [*회원ID, 이름, 회원ID (FK)]' → 엔터티 카드. *는 PK, (FK)는 FK. 'part_no (품번)'처럼 괄호는 한글명."""
    m = re.match(r"\s*(.*?)\s*(?:@([\w:+-]+))?\s*(?:\[(.*)\])?\s*$", spec)
    name, ic, attrs = m.group(1), m.group(2), m.group(3)
    if ic is None and attrs is None and name in known:
        return known[name].replace("--i:X", "--i:%d" % i)
    lis = ""
    if attrs:
        for a in [x.strip() for x in attrs.split(",") if x.strip()]:
            pk, fk = a.startswith("*"), a.endswith("(FK)")
            a = a.lstrip("*").replace("(FK)", "").strip()
            tag = ('<em class="k-pk">PK</em>' if pk else "") + ('<em class="k-fk">FK</em>' if fk else "")
            lis += '<li class="%s">%s<span>%s</span></li>' % ("pk" if pk else "fk" if fk else "", tag, erd_label(a))
    card = '<div class="erd-ent" style="--i:X"><div class="erd-name">%s<span>%s</span></div>%s</div>' % (
        '<span class="ic-inline">%s</span>' % icon_svg(ic) if ic else "", erd_label(name), "<ul>%s</ul>" % lis if lis else "")
    known[name] = card
    return card.replace("--i:X", "--i:%d" % i)


def erd_link(spec, i, w, flip=False):
    """flip: 왼쪽으로 뻗는 팔. '||--o<'를 거울에 비춘 '>o--||'로 그린다."""
    code, _, verb = spec.strip().partition(" ")
    if flip:
        code = code[::-1].translate(str.maketrans("<>", "><"))
    return '<div class="erd-link" style="--i:%d"><span class="erd-verb">%s</span>%s</div>' % (i, render_inline(verb.strip()), erd_line_svg(code, w))


def render_erd(b):
    """ERD 그림. 한 줄에: 엔터티 ; 선 관계명 ; 엔터티 (; 선 ; 엔터티 … 이어 붙이기)
    모든 줄의 첫 엔터티가 같으면 가운데 하나에서 여러 개로 뻗는 모양이 된다.
    4줄 이상이면 앞의 절반은 왼쪽, 나머지는 오른쪽으로 나눠 뻗는다."""
    lines = [[x.strip() for x in l.split(";")] for l in b["body"].splitlines() if l.strip()]
    known, rows = {}, []
    firsts = {re.match(r"\s*(.*?)\s*(?:@|\[|$)", l[0]).group(1) for l in lines}
    if len(lines) > 1 and len(firsts) == 1 and all(len(l) == 3 for l in lines):
        hub = erd_entity(lines[0][0], known, 0)
        split = len(lines) // 2 if len(lines) >= 4 else 0

        def arm(n, l, flip):
            link, ent = erd_link(l[1], 2 * n + 1, 150, flip), erd_entity(l[2], known, 2 * n + 2)
            return '<div class="erd-arm">%s</div>' % (ent + link if flip else link + ent)
        left = "".join(arm(n, l, True) for n, l in enumerate(lines[:split]))
        right = "".join(arm(n + split, l, False) for n, l in enumerate(lines[split:]))
        left = '<div class="erd-arms erd-arms-l">%s</div>' % left if left else ""
        return '<figure class="erd"><div class="erd-star%s">%s<div class="erd-hub">%s</div><div class="erd-arms">%s</div></div>%s</figure>' % (
            " erd-star-2" if left else "", left, hub, right, caption(b))
    for l in lines:
        parts, k = [], 0
        for j, f in enumerate(l):
            parts.append(erd_entity(f, known, k) if j % 2 == 0 else erd_link(f, k, 220 if len(l) <= 3 else 150))
            k += 1
        rows.append('<div class="erd-row">%s</div>' % "".join(parts))
    return '<figure class="erd">%s%s</figure>' % ("".join(rows), caption(b))


def render_flow(b):
    steps, op, i = [], "→", 0
    for line in b["body"].splitlines():
        if not line.strip():
            continue
        if line.strip() in ("+", "=", "→", "×"):
            op = line.strip()
            continue
        ic, title, desc, tone = fields(line, 4)
        cls, style = tone_attrs(tone, "ivory")
        sep = '<span class="flow-op" aria-hidden="true">%s</span>' % op if steps else ""
        steps.append('<li class="flow-step frag tone-%s" style="%s--i:%d">%s%s<b>%s</b>%s</li>' % (
            cls, style, i, sep, bubble(ic), render_inline(title),
            '<span class="d">%s</span>' % render_inline(desc) if desc else ""))
        op, i = "→", i + 1
    return '<figure class="flow"><ol class="flow-row">%s</ol>%s</figure>' % ("".join(steps), caption(b))


def render_bars(b):
    """가로 막대그래프. 머리 줄: 'series: A | B', 선택 'unit: %', 'scale: 100'. 나머지 줄: 항목 | 값A | 값B"""
    opts, rows = {}, []
    for line in b["body"].splitlines():
        m = re.match(r"\s*(series|unit|scale)\s*:\s*(.*)", line)
        if m:
            opts[m.group(1)] = m.group(2).strip()
        elif line.strip():
            rows.append([x.strip() for x in line.split("|")])
    series = [s.strip() for s in opts["series"].split("|")]
    unit = opts.get("unit", "")
    scale = float(opts.get("scale") or (100 if unit == "%" else max(float(v) for r in rows for v in r[1:])))
    legend = "".join('<li><i class="s%d"></i>%s</li>' % (k, esc(s)) for k, s in enumerate(series))
    groups, n = [], 0
    for r in rows:
        bars = []
        for k, v in enumerate(r[1:]):
            bars.append('<div class="bar-row" title="%s · %s: %s%s"><span class="bar s%d" style="--w:%.2f%%;--i:%d"></span>'
                        '<span class="bar-v">%s%s</span></div>' % (esc(r[0]), esc(series[k]), v, unit, k, float(v) / scale * 100, n, v, unit))
            n += 1
        groups.append('<div class="bars-group"><div class="bars-label">%s</div>%s</div>' % (render_inline(r[0]), "".join(bars)))
    table = '<table class="sr-only"><thead><tr><th>항목</th>%s</tr></thead><tbody>%s</tbody></table>' % (
        "".join("<th>%s</th>" % esc(s) for s in series),
        "".join("<tr><th>%s</th>%s</tr>" % (esc(r[0]), "".join("<td>%s%s</td>" % (v, unit) for v in r[1:])) for r in rows))
    return '<figure class="bars"><ul class="bars-legend">%s</ul>%s%s%s</figure>' % (legend, "".join(groups), table, caption(b))


def render_hub(b):
    """가운데 DB와 양옆 팀. 한 줄에: 아이콘 | 이름 | left·center·right. 가운데 → 왼쪽 → 오른쪽 순서로 나타난다."""
    side = {"left": [], "center": [], "right": []}
    for line in b["body"].splitlines():
        if line.strip():
            ic, label, where = fields(line, 3)
            side[where or "left"].append((ic, label))
    node = lambda ic, label, tone: '<div class="hub-node tone-%s">%s<b>%s</b></div>' % (tone, bubble(ic), render_inline(label))
    link = '<div class="hub-link" aria-hidden="true"><span class="l1"></span><span class="l2"></span></div>'
    center = "".join(node(ic, label, "plum") for ic, label in side["center"])
    left = "".join(node(ic, label, "ivory") for ic, label in side["left"])
    right = "".join(node(ic, label, "ivory") for ic, label in side["right"])
    parts = ['<div class="hub-center frag" style="--i:0">%s</div>' % center]
    if left:
        parts.insert(0, '<div class="hub-side frag" style="--i:1"><div class="hub-col">%s</div>%s</div>' % (left, link))
    if right:
        parts.append('<div class="hub-side frag" style="--i:2">%s<div class="hub-col">%s</div></div>' % (link, right))
    return '<figure class="hub">%s%s</figure>' % ("".join(parts), caption(b))


def render_compare(b):
    rows = [l for l in b["body"].splitlines() if l.strip()]
    out = []
    for i, line in enumerate(rows):
        left, _, right = line.partition("||")
        cells = []
        for side, part in (("left", left), ("right", right)):
            ic, text = fields(part, 2)
            cells.append('<div class="cmp-cell cmp-%s">%s<span>%s</span></div>' % (side, bubble(ic), render_inline(text)))
        if i == 0:
            out.append('<div class="cmp-row cmp-head">%s<div class="cmp-mid">vs</div>%s</div>' % tuple(cells))
        else:
            out.append('<div class="cmp-row frag" style="--i:%d">%s<div class="cmp-mid" aria-hidden="true">→</div>%s</div>' % (i - 1, cells[0], cells[1]))
    return '<figure class="compare">%s%s</figure>' % ("".join(out), caption(b))


def hl(code, lang):
    try:
        lexer = get_lexer_by_name(lang or "text")
    except ClassNotFound:
        lexer = get_lexer_by_name("text")
    return highlight(code, lexer, HtmlFormatter(nowrap=True)).rstrip("\n")


LANG_NAMES = {"sql": "SQL", "python": "Python", "bash": "터미널", "sh": "터미널", "text": "도식",
              "json": "JSON", "dbml": "DBML", "screen": "화면"}  # screen: 터미널 화면 예시(색 없이)


def render_code(b):
    label = LANG_NAMES.get(b["lang"], b["lang"] or "코드")
    if b["caption"]:
        label += " · " + esc(b["caption"])
    return ('<figure class="code"><div class="code-head"><span>%s</span><button type="button" class="copy">복사</button></div>'
            '<pre class="hl"><code>%s</code></pre></figure>' % (label, hl(b["body"], b["lang"])))


def render_result(b, error=False):
    body = b["body"].strip()
    if body.startswith("|"):
        rows = max(0, len([l for l in body.splitlines() if l.strip().startswith("|")]) - 2)
        inner, side = render_md(body), '<span class="rows">%d rows</span>' % rows
    else:
        inner, side = "<pre><code>%s</code></pre>" % esc(body), ""
    label = "오류 메시지" if error else "실행 결과"
    if b["caption"]:
        label += " · " + esc(b["caption"])
    return '<figure class="output%s"><div class="code-head"><span>%s</span>%s</div>%s</figure>' % (
        " is-error" if error else "", label, side, inner)


def render_shot(b):
    """화면 캡처. 경로가 없으면 나중에 찍어 넣을 자리를 표시한다."""
    src = b["body"].strip()
    if not src:
        return ('<figure class="shot shot-todo"><div class="shot-todo-box">%s<b>캡처 필요</b><span>%s</span></div></figure>'
                % (icon_svg("image-plus"), render_inline(b["caption"])))
    if not (ROOT / "images" / src).exists():
        raise SystemExit("캡처 파일이 없습니다: images/%s" % src)
    return '<figure class="shot"><img src="images/%s" alt="%s" loading="lazy">%s</figure>' % (
        esc(src), esc(b["caption"]), caption(b))


def render_stepper(b):
    data = json.loads(b["body"])
    code_lines = data["code"].split("\n")
    lis = "".join('<li><span class="ln">%d</span><code>%s</code></li>' % (n + 1, hl(l, data.get("lang", "sql")) or " ")
                  for n, l in enumerate(code_lines))
    return ('<figure class="stepper" data-steps="%s"><div class="stepper-title">%s</div>'
            '<div class="stepper-body"><ol class="stepper-code hl">%s</ol>'
            '<div class="stepper-side"><div class="side-label">중간 결과</div><div class="stepper-table"></div></div></div>'
            '<p class="stepper-note"></p>'
            '<div class="stepper-ctrl"><span class="stepper-count"></span>'
            '<button type="button" data-act="reset">처음</button><button type="button" data-act="prev">이전</button>'
            '<button type="button" data-act="next" class="primary">다음</button><button type="button" data-act="play">자동 재생</button>'
            '</div></figure>') % (esc(json.dumps(data["steps"], ensure_ascii=False)),
                                  esc(data.get("title", "실행 순서 따라가기")), lis)


def render_quiz(b):
    parts = re.split(r"^Q\.\s*", b["body"].strip(), flags=re.M)
    out = []
    for p in parts:
        if not p.strip():
            continue
        q, _, a = p.partition("\nA.")
        out.append('<div class="q">%s<details><summary>정답 보기</summary><div class="a">%s</div></details></div>'
                   % (render_md(q.strip()), render_md(a.strip())))
    return "".join(out)


def render_block(b):
    k = b["kind"]
    if k == "para":
        return render_md(b["text"])
    if k == "fence":
        if b["lang"] == "result":
            return render_result(b)
        if b["lang"] == "error":
            return render_result(b, error=True)
        if b["lang"] == "mermaid":
            cap = '<figcaption>%s</figcaption>' % esc(b["caption"]) if b["caption"] else ""
            return '<figure class="fig fig-mmd"><div class="fig-stage"><pre class="mermaid">%s</pre></div>%s</figure>' % (esc(b["body"]), cap)
        if b["lang"] == "stepper":
            return render_stepper(b)
        if b["lang"] in ("icons", "icons-lg", "icons-def"):
            return render_icons(b)
        if b["lang"] == "rows":
            return render_rows(b)
        if b["lang"] == "erd":
            return render_erd(b)
        if b["lang"] == "stats":
            return render_stats(b)
        if b["lang"] == "flow":
            return render_flow(b)
        if b["lang"] == "compare":
            return render_compare(b)
        if b["lang"] == "bars":
            return render_bars(b)
        if b["lang"] == "hub":
            return render_hub(b)
        if b["lang"] == "shot":
            return render_shot(b)
        return render_code(b)
    if k == "box" and b["box"] == "window":
        return ('<div class="win"><div class="win-dots" aria-hidden="true"><i></i><i></i><i></i></div><div class="win-body">'
                '<div class="win-head"><span class="win-chip">DB</span>%s</div><div class="win-main">%s</div></div></div>') % (
            render_inline(b["title"]), "".join(render_block(c) for c in b["children"]))
    if k == "box" and b["box"] == "cols":
        return '<div class="cols">%s</div>' % "".join(render_block(c) for c in b["children"])
    if k == "box" and b["box"] == "center":
        return '<div class="center-block">%s</div>' % "".join(render_block(c) for c in b["children"])
    if k == "box" and b["box"] == "answer":
        return '<details class="answer"><summary>%s</summary><div class="answer-body">%s</div></details>' % (
            esc(b["title"] or BOX_LABELS["answer"]), "".join(render_block(c) for c in b["children"]))
    if k == "box":
        label = BOX_LABELS.get(b["box"], b["box"])
        title = '<div class="box-title">%s</div>' % esc(b["title"]) if b["title"] else ""
        inner = render_quiz(b) if b["box"] == "quiz" else "".join(render_block(c) for c in b["children"])
        return '<aside class="box box-%s"><div class="box-label">%s</div>%s%s</aside>' % (b["box"], label, title, inner)
    return ""


# ---------------------------------------------------------------- 공통 조각

def head(title, depth, extra=""):
    up = "../" * depth
    return ('<!doctype html>\n<html lang="ko"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1"><title>%s</title>'
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">'
            '<link rel="stylesheet" href="%sassets/style.css">%s</head>\n') % (esc(title), up, extra)


MERMAID = '<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>'


def scripts(depth, has_mermaid, slides=False):
    up = "../" * depth
    s = (MERMAID if has_mermaid else "") + '<script src="%sassets/common.js"></script>' % up
    if slides:
        s += '<script src="%sassets/slides.js"></script>' % up
    return s


# ---------------------------------------------------------------- 교재 페이지

def day_label(meta):
    return meta.get("label", "")


def build_textbook(day, course, nav):
    blocks = day["blocks"]
    toc, body, chapters = [], [], []
    for b in blocks:
        if b["kind"] == "h":
            lv, t = b["level"], esc(b["text"])
            body.append('<h%d id="%s" class="reveal">%s</h%d>' % (lv, b["id"], t, lv))
            if lv <= 2:
                toc.append('<li class="toc-h%d"><a href="#%s">%s</a></li>' % (lv, b["id"], t))
            if lv == 1:
                chapters.append(b)
        elif b["kind"] != "break":
            body.append('<div class="reveal">%s</div>' % render_block(b))

    hero = ('<header class="day-hero"><p class="day-meta"><span class="day-num">%s</span>%s</p>'
            '<h1 class="day-title">%s</h1><ol class="day-chapters">%s</ol></header>') % (
        esc(day_label(day["meta"])), esc(day["meta"].get("date", "")), esc(day["title"]),
        "".join('<li><a href="#%s">%s</a></li>' % (c["id"], esc(c["text"])) for c in chapters))
    prev_, next_ = nav
    day_nav = '<nav class="day-nav">%s%s</nav>' % (
        '<a href="%s.html"><span class="dir">이전 단원</span><span class="t">%s</span></a>' % (prev_["id"], esc(prev_["title"])) if prev_ else "<span></span>",
        '<a class="next" href="%s.html"><span class="dir">다음 단원</span><span class="t">%s</span></a>' % (next_["id"], esc(next_["title"])) if next_ else "")

    page = head("%s · %s" % (day_label(day["meta"]), day["title"]), 0)
    page += ('<body class="book-page"><div class="progress"><span></span></div>'
             '<header class="topbar"><button type="button" class="toc-toggle" aria-expanded="false" aria-controls="toc">목차</button>'
             '<a class="home-link" href="index.html">과정 목차</a><span class="topbar-title">%s</span>'
             '<a class="home-link" href="slides/%s.html">슬라이드로 보기</a>'
             '<button type="button" class="motion-toggle" aria-pressed="false">모션 끄기</button></header>'
             '<nav class="toc" id="toc"><p class="toc-course"><a href="index.html">%s</a></p><ol>%s</ol></nav>'
             '<main class="content">%s<div class="chapter">%s</div>%s'
             '<footer class="page-foot"><p>%s</p></footer></main>%s</body></html>') % (
        esc(day["title"]), day["id"], esc(course["title"]), "".join(toc), hero, "".join(body), day_nav,
        esc(course["meta"]), scripts(0, day["has_mermaid"]))
    (DIST / ("%s.html" % day["id"])).write_text(page, encoding="utf-8")


# ---------------------------------------------------------------- 슬라이드

def cost(b):
    """블록이 슬라이드에서 차지할 대략적인 줄 수."""
    k = b["kind"]
    if k == "para":
        text = re.sub(r"\s+", " ", re.sub(r"\]\([^)]*\)", "]", b["text"]))  # 링크 주소는 화면에 안 보이므로 빼고 잰다
        return max(b["text"].count("\n") + 1, math.ceil(len(text) / 46)) + 0.4
    if k == "fence":
        if b["lang"] == "mermaid":
            return 10
        if b["lang"] in ("result", "error"):
            return b["body"].count("\n") * 0.9 + 2
        if b["lang"] == "icons":
            return 5.5
        if b["lang"] in ("icons-lg", "icons-def"):
            return 14
        if b["lang"] == "rows":
            return (b["body"].count("\n") + 1) * 1.7 + 1
        if b["lang"] == "erd":
            ls = [l for l in b["body"].splitlines() if l.strip()]
            attrs = max([l.count(",") + 1 if "[" in l else 0 for l in ls] + [0])
            return (len(ls) * 3 if len(ls) > 1 and len({l.split(";")[0].split("@")[0].split("[")[0].strip() for l in ls}) == 1 else len(ls) * 2.5) + attrs * 1.1 + 1.5
        if b["lang"] == "stats":
            return 5
        if b["lang"] == "flow":
            return 6
        if b["lang"] == "compare":
            return (b["body"].count("\n") + 1) * 1.9 + 1
        if b["lang"] == "bars":
            return b["body"].count("\n") * 2.2 + 2
        if b["lang"] == "hub":
            return 7
        if b["lang"] == "shot":
            return 12 if b["body"].strip() else 4
        if b["lang"] == "stepper":
            return 99
        return b["body"].count("\n") + 2.5
    if k == "box":
        if b["box"] == "quiz":
            return 99
        if b["box"] == "cols":
            return max(cost(c) for c in b["children"])
        if b["box"] == "answer":
            return 1.5  # 접힌 상태 기준. 펼치면 slides.js 가 다시 맞춘다.
        return 1.5 + sum(cost(c) for c in b["children"])
    return 0


def paginate(blocks):
    """제목과 블록을 슬라이드 목록으로 바꾼다."""
    slides = []
    state = {"crumb": "", "title": "", "sid": "", "page": 0}
    cur, used = [], 0.0

    def flush():
        nonlocal cur, used
        if cur:
            kinds = {(b["kind"], b.get("lang") or b.get("box")) for b in cur}
            kind = "quiz" if ("box", "quiz") in kinds else "visual" if kinds & {("fence", "mermaid"), ("fence", "stepper")} else "flow"
            slides.append({"type": "content", "kind": kind, "blocks": cur, "crumb": state["crumb"],
                           "title": state["title"], "cont": state["page"] > 0, "sid": state["sid"]})
            state["page"] += 1
        cur, used = [], 0.0

    for b in blocks:
        if b["kind"] == "h":
            flush()
            lv = b["level"]
            if lv == 1:
                state["chapter"] = b["text"]
                state.update(crumb="", title=b["text"])
                slides.append({"type": "chapter", "title": b["text"], "sid": b["id"]})
            elif lv == 2:
                state.update(crumb=state.get("chapter", ""), title=b["text"])
                slides.append({"type": "section", "title": b["text"], "crumb": state.get("chapter", ""), "sid": b["id"]})
            else:
                state["title"] = b["text"]
            state.update(sid=b["id"], page=0, keep=b["keep"])
            continue
        if b["kind"] == "break":
            flush()
            continue
        if b["kind"] == "box" and b["box"] == "teacher":
            continue
        # 코드 바로 뒤의 실행 결과는 같은 슬라이드에 붙인다.
        if (b["kind"] == "fence" and b["lang"] in ("result", "error") and cur
                and cur[-1]["kind"] == "fence" and cur[-1]["lang"] not in ("result", "error", "mermaid", "stepper")):
            cur.append(b)
            used += cost(b)
            continue
        c = cost(b)
        # 짧은 도입 문단(INTRO 줄 이하)만 있으면 다음 블록과 떼지 않는다. 넘치는 만큼은 fit()이 줄인다.
        keep = state.get("keep")  # 제목에 {keep}: 나누지 않고 한 장에 담는다(넘치면 fit()이 줄인다)
        if used + c > SLIDE_BUDGET and used > INTRO and not keep:
            flush()
        cur.append(b)
        used += c
        if c >= SLIDE_BUDGET and not keep:
            flush()
    flush()
    return slides


def build_slides(day, course):
    meta, slides = day["meta"], paginate(day["blocks"])
    total = len(slides) + 2
    foot_l = "%s · %s" % (day_label(meta), day["title"])
    foot = lambda n: '<footer class="s-foot"><span>%s</span><span>%d / %d</span></footer>' % (esc(foot_l), n, total)

    chapters = [b for b in day["blocks"] if b["kind"] == "h" and b["level"] == 1]
    out = ['<section class="slide t-title" data-sid=""><p class="tt-meta"><span class="tt-day">%s</span>%s</p>'
           '<h1>%s</h1><ol>%s</ol><p class="tt-course">%s</p><div class="tt-swatch"><i></i><i></i><i></i><i></i></div>%s</section>'
           % (esc(day_label(meta)), esc(meta.get("date", "")), esc(day["title"]),
              "".join("<li>%s</li>" % esc(c["text"]) for c in chapters), esc(course["title"]), foot(1))]
    options = ['<option value="0">%s 표지</option>' % esc(day_label(meta))]

    for n, s in enumerate(slides, start=1):
        if s["type"] == "chapter":
            options.append('<option value="%d">%s</option>' % (n, esc(s["title"])))
            out.append('<section class="slide t-chapter" data-sid="%s"><h1>%s</h1>%s</section>' % (s["sid"], esc(s["title"]), foot(n + 1)))
        elif s["type"] == "section":
            options.append('<option value="%d">　%s</option>' % (n, esc(s["title"])))
            out.append('<section class="slide t-section" data-sid="%s"><p class="s-crumb">%s</p><h2>%s</h2>%s</section>'
                       % (s["sid"], esc(s["crumb"]), esc(s["title"]), foot(n + 1)))
        else:
            crumb = '<p class="s-crumb">%s</p>' % esc(s["crumb"]) if s["crumb"] else ""
            cont = '<span class="s-cont">이어서</span>' if s["cont"] else ""
            out.append('<section class="slide kind-%s" data-sid="%s">%s<h2 class="s-title">%s%s</h2>'
                       '<div class="s-body"><div class="s-fit">%s</div></div>%s</section>'
                       % (s["kind"], s["sid"], crumb, esc(s["title"]), cont, "".join(render_block(b) for b in s["blocks"]), foot(n + 1)))

    out.append('<section class="slide t-end" data-sid=""><h2>오늘 수업은 여기까지입니다</h2><div class="end-links">'
               '<a href="../%s.html">교재로 복습하기</a><a href="index.html">슬라이드 목록</a></div>%s</section>' % (day["id"], foot(total)))

    page = head("%s · 슬라이드" % foot_l, 1)
    page += ('<body class="slides-page"><header class="s-bar"><a href="index.html">슬라이드 목록</a>'
             '<span class="s-bar-title">%s</span><select class="s-jump" aria-label="장·차시로 이동">%s</select>'
             '<a class="s-book" href="../%s.html">교재에서 보기</a>'
             '<button type="button" class="motion-toggle" aria-pressed="false">모션 끄기</button>'
             '<button type="button" class="s-full" title="전체 화면(F)">전체 화면</button>'
             '<button type="button" class="s-prev" aria-label="이전 슬라이드">◀</button>'
             '<button type="button" class="s-next" aria-label="다음 슬라이드">▶</button></header>'
             '<div class="stage"><div class="deck" data-day="%s">%s</div></div>%s</body></html>') % (
        esc(foot_l), "".join(options), day["id"], day["id"], "\n".join(out).replace('src="images/', 'src="../images/'), scripts(1, day["has_mermaid"], slides=True))
    (DIST / "slides" / ("%s.html" % day["id"])).write_text(page, encoding="utf-8")


# ---------------------------------------------------------------- 과정 목차

def build_indexes(course, days):
    def cards(target):
        groups = []
        for g in course["groups"]:
            items = []
            for d in g["units"]:
                info = days.get(d["id"])
                title = info["title"] if info else d.get("title", "")
                date = info["meta"].get("date", "") if info else ""
                num = day_label(info["meta"]) if info else d.get("label", "")
                chs = " · ".join(b["text"] for b in info["blocks"] if b["kind"] == "h" and b["level"] == 1) if info else "준비 중"
                inner = '<span class="when">%s<small>%s</small></span><span class="ttl">%s</span><span class="chs">%s</span>' % (
                    esc(num), esc(date), esc(title), esc(chs))
                items.append('<li class="day-card">%s</li>' % (
                    '<a href="%s.html">%s</a>' % (d["id"], inner) if info else '<span class="disabled">%s</span>' % inner))
            groups.append('<section class="subject-group"><h2>%s</h2><ul class="day-cards">%s</ul></section>' % (esc(g["name"]), "".join(items)))
        return "".join(groups)

    # 강사 소개: instructor.md 가 있으면 목차 맨 위에 작은 버튼과 팝업을 붙인다.
    instructor = ""
    ins_file = ROOT / "instructor.md"
    if ins_file.exists():
        ins_meta, ins_text = read_front_matter(ins_file.read_text(encoding="utf-8"))
        ins_body = "".join(render_block(b) for b in parse_blocks(ins_text))
        instructor = (
            '<p class="instructor-open"><button type="button" class="home-link" '
            'onclick="document.getElementById(\'instructor\').showModal()">%s강사 소개</button></p>'
            '<dialog id="instructor" class="instructor-dlg" aria-labelledby="instructor-name" '
            'onclick="if(event.target===this)this.close()"><div class="instructor-inner">'
            '<header><div><p class="instructor-role">%s</p><h2 id="instructor-name">%s</h2></div>'
            '<button type="button" class="instructor-x" aria-label="닫기" onclick="this.closest(\'dialog\').close()">%s</button></header>'
            '%s</div></dialog>') % (icon_svg("user-round"), esc(ins_meta.get("role", "")), esc(ins_meta.get("name", "")),
                                    icon_svg("x"), ins_body)

    for depth, target, title, lead in (
        (0, DIST / "index.html", course["title"], '단원을 눌러 교재를 엽니다. <a href="slides/index.html">슬라이드 목록으로 가기</a>'),
        (1, DIST / "slides" / "index.html", course["title"] + " — 슬라이드",
         '단원을 눌러 슬라이드를 엽니다. 방향키(←·→)로 넘기고, F 키로 전체 화면을 켭니다. <a href="../index.html">교재 목차로 가기</a>'),
    ):
        page = head(title, depth)
        page += ('<body class="index-page"><main class="content"><header class="course-hero"><p class="day-meta">%s</p>'
                 '<h1>%s</h1><p>%s</p>%s<div class="tt-swatch"><i></i><i></i><i></i><i></i></div></header>%s'
                 '<footer class="page-foot"><p>%s</p></footer></main></body></html>') % (
            esc(course["meta"]), esc(title), lead, instructor, cards(target), esc(course["meta"]))
        target.write_text(page, encoding="utf-8")


# ---------------------------------------------------------------- 실행

def main():
    course = json.loads((ROOT / "course.json").read_text(encoding="utf-8"))
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "slides").mkdir(parents=True)
    shutil.copytree(ROOT / "assets", DIST / "assets")
    if (ROOT / "images").exists():
        shutil.copytree(ROOT / "images", DIST / "images")

    days = {}
    for f in sorted(CONTENT.glob("*.md")):
        meta, text = read_front_matter(f.read_text(encoding="utf-8"))
        blocks = parse_blocks(text)
        assign_ids(blocks)
        days[f.stem] = {"id": f.stem, "meta": meta, "title": meta.get("title", f.stem), "blocks": blocks,
                        "has_mermaid": "```mermaid" in text}

    order = [d["id"] for g in course["groups"] for d in g["units"] if d["id"] in days]
    for n, did in enumerate(order):
        prev_ = days[order[n - 1]] if n > 0 else None
        next_ = days[order[n + 1]] if n + 1 < len(order) else None
        build_textbook(days[did], course, (prev_, next_))
        build_slides(days[did], course)
        print("built", did)
    build_indexes(course, days)
    print("done → %s" % DIST)


if __name__ == "__main__":
    main()
