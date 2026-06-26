#!/usr/bin/env python3
"""render-qa.py — drafts/qa-{id}.md → site/qa/{id}.html
마크다운 규칙은 render-briefing.py와 동일 (LEAD, 각주, 한국 관점).
사용: python3 scripts/render-qa.py --id qa-001
     (approval_gate.py 승인 시 render-qa.sh 경유 자동 호출)
"""
import argparse, json, re, subprocess
from datetime import date
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent


# ─────────────────────────────────────────────
# 인라인 변환 (render-briefing.py와 동일)
# ─────────────────────────────────────────────

def inline_md(text):
    text = re.sub(r'\[\^(\d+)\]', r'<sup>\1</sup>', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    return text


# ─────────────────────────────────────────────
# 본문 변환 (render-briefing.py와 동일)
# ─────────────────────────────────────────────

def md_body_to_html(md_text):
    lines = md_text.split('\n')
    html = []
    notes = []
    in_front = False
    in_lead = False
    in_notes_def = False
    in_list = False
    skip_sections = {'편집 메모'}
    skip_active = False

    for i, raw in enumerate(lines):
        line = raw.rstrip()

        if i == 0 and line.strip() == '---':
            in_front = True; continue
        if in_front:
            if line.strip() == '---': in_front = False
            continue

        if line.strip() == '<!-- LEAD -->':
            if in_list: html.append('</ul>'); in_list = False
            html.append('<div class="lead">')
            in_lead = True; continue
        if line.strip() == '<!-- /LEAD -->':
            html.append('</div>')
            in_lead = False; continue

        if in_lead:
            if line.startswith('> '):
                html.append(f'  <p>{inline_md(line[2:].strip())}</p>')
            elif line.strip():
                html.append(f'  <p>{inline_md(line.strip())}</p>')
            continue

        if line.startswith('# '): continue

        if line.startswith('## '):
            if in_list: html.append('</ul>'); in_list = False
            sec = line[3:].strip()
            in_notes_def = '주 (' in sec or '註' in sec or sec.startswith('주')
            skip_active = any(s in sec for s in skip_sections)
            if not skip_active and not in_notes_def:
                html.append(f'<h2 class="serif">{inline_md(sec)}</h2>')
            continue

        if skip_active: continue

        if in_notes_def and re.match(r'\[\^\d+\]:', line):
            m = re.match(r'\[\^(\d+)\]:\s*(.*)', line)
            if m:
                notes.append((m.group(1), inline_md(m.group(2))))
            continue

        if line.startswith('### '):
            if in_list: html.append('</ul>'); in_list = False
            html.append(f'<h3>{inline_md(line[4:].strip())}</h3>'); continue

        if line.strip() == '---':
            if in_list: html.append('</ul>'); in_list = False
            html.append('<hr>'); continue

        if line.startswith('- '):
            if not in_list: html.append('<ul>'); in_list = True
            html.append(f'  <li>{inline_md(line[2:].strip())}</li>'); continue

        if line.startswith('> '):
            if in_list: html.append('</ul>'); in_list = False
            html.append(f'<blockquote><p>{inline_md(line[2:].strip())}</p></blockquote>'); continue

        if not line.strip():
            if in_list: html.append('</ul>'); in_list = False
            html.append(''); continue

        if in_list: html.append('</ul>'); in_list = False
        if in_notes_def: continue
        html.append(f'<p>{inline_md(line.strip())}</p>')

    if in_list:
        html.append('</ul>')

    if notes:
        html.append('<div class="notes">')
        html.append('  <h4>주 (註)</h4>')
        html.append('  <ol>')
        for num, text in sorted(notes, key=lambda x: int(x[0])):
            html.append(f'    <li>{text}</li>')
        html.append('  </ol>')
        html.append('  <div class="meta">공개 자료 기반, 출처 명기 (헌법 0조 부칙).</div>')
        html.append('</div>')

    return '\n'.join(html)


# ─────────────────────────────────────────────
# Q&A 파싱
# ─────────────────────────────────────────────

def parse_qa_draft(md_text):
    """프론트매터에서 id, question, category, date 추출."""
    qa_id = question = ""
    category = "기타"
    pub_date = date.today().isoformat()

    fm_m = re.match(r'^---\n(.*?)\n---', md_text, re.DOTALL)
    if fm_m:
        for line in fm_m.group(1).splitlines():
            if ':' not in line:
                continue
            key, val = line.split(':', 1)
            key, val = key.strip(), val.strip()
            if key == 'id':
                qa_id = val
            elif key == 'question':
                question = val
            elif key == 'category':
                category = val
            elif key == 'created':
                pub_date = val

    title_m = re.search(r'^# (.+)$', md_text, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else question[:60] or qa_id

    return qa_id, question, category, pub_date, title


# ─────────────────────────────────────────────
# HTML 페이지 생성
# ─────────────────────────────────────────────

def build_html(qa_id, question, category, pub_date, title, body_html):
    y, mo, d = pub_date.split('-')
    date_kr = f"{y}년 {int(mo)}월 {int(d)}일"
    q_escaped = question.replace('"', '&quot;')

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · 철강 주재원 Q&amp;A</title>
<meta name="description" content="{q_escaped}">
<meta name="sa-title" content="{title}">
<meta name="sa-summary" content="{q_escaped}">
<meta name="sa-category" content="Q&amp;A">
<meta name="sa-date" content="{pub_date}">
<meta name="sa-featured" content="">
<meta name="sa-thumb" content="">
<meta name="sa-author" content="편집실">
<link rel="stylesheet" href="../style.css">
</head>
<body>
<header class="masthead"><div class="wrap">
  <div class="mh-brand">
    <svg class="mh-mark" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect x="1" y="1" width="38" height="38" rx="9" fill="#11161d" stroke="#3a4654"/><path d="M20 8 L31 30 H9 Z" fill="none" stroke="#D62828" stroke-width="2.4" stroke-linejoin="round"/><path d="M20 20 L26 30 H14 Z" fill="#D62828"/><circle cx="20" cy="26.5" r="1.7" fill="#ffd9a8"/></svg>
    <div class="mh-title"><a href="../index.html">철강 주재원</a><span class="sub">Steel Attaché</span></div>
  </div>
  <nav class="mh-nav"><a href="../index.html">홈</a><a href="../qa.html">Q&amp;A</a></nav>
</div></header>

<main class="col">
<article>
  <a class="back" href="../qa.html">← Q&amp;A 목록</a>
  <div class="eyebrow">Q&amp;A · {category}</div>
  <h1 class="serif">{title}</h1>
  <div class="byline">
    <span class="q-badge">질문</span> {question}
  </div>
  <div class="byline">철강 주재원 · {date_kr} · 편집실</div>

  <div class="article-body">
{body_html}
  </div>
</article>
</main>

<footer class="foot"><div class="wrap">
  <div class="b">철강 주재원</div>
  <div class="s">포스코의 눈으로 읽는 세계 철강 분석 · © {y} · 공개 자료 기반, 출처 명기</div>
</div></footer>
</body>
</html>"""


# ─────────────────────────────────────────────
# questions.json 갱신
# ─────────────────────────────────────────────

def update_questions(qa_id, pub_date):
    q_path = SITE_DIR / "data" / "questions.json"
    if not q_path.exists():
        return
    questions = json.loads(q_path.read_text(encoding="utf-8"))
    updated = False
    for q in questions:
        if q.get("id") == qa_id:
            q["status"] = "published"
            q["published"] = pub_date
            q["url"] = f"qa/{qa_id}.html"
            updated = True
    if updated:
        q_path.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ questions.json 갱신: {qa_id} → published")
    else:
        print(f"⚠️ questions.json에 {qa_id} 항목 없음 — 수동 확인 필요")


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Q&A 초안 → HTML 렌더")
    parser.add_argument('--id', required=True, help='Q&A ID (예: qa-001)')
    args = parser.parse_args()
    qa_id = args.id

    draft_path = SITE_DIR.parent / "drafts" / f"{qa_id}.md"
    if not draft_path.exists():
        print(f"❌ 초안 없음: {draft_path}")
        raise SystemExit(1)

    md_text = draft_path.read_text(encoding="utf-8")
    qa_id_parsed, question, category, pub_date, title = parse_qa_draft(md_text)
    effective_id = qa_id_parsed or qa_id

    body_html = md_body_to_html(md_text)
    html = build_html(effective_id, question, category, pub_date, title, body_html)

    out_path = SITE_DIR / "qa" / f"{effective_id}.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"✅ HTML 렌더 완료: {out_path}")

    update_questions(effective_id, pub_date)


if __name__ == "__main__":
    main()
