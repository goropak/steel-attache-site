#!/usr/bin/env python3
"""render-briefing.py — draft .md → posts/briefing-YYYY-MM-DD.html
사용: python3 scripts/render-briefing.py --date YYYY-MM-DD
     (approval_gate.py 승인 시 render-briefing.sh 경유로 자동 호출)
"""
import argparse
import re
import subprocess
from datetime import date, timedelta
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent


# ─────────────────────────────────────────────
# 파싱
# ─────────────────────────────────────────────

def parse_draft(md_text):
    """draft md에서 날짜, 타이틀, 게시 수, 뉴스 수 추출."""
    pub_date = date.today().isoformat()
    m = re.search(r'작성일:\s*(\d{4}-\d{2}-\d{2})', md_text)
    if m:
        pub_date = m.group(1)

    title_m = re.search(r'^# (.+)$', md_text, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else f"주간 브리핑 {pub_date}"

    post_m = re.search(r'## 이번 주 게시.*?[(（](\d+)건[)）]', md_text)
    post_count = int(post_m.group(1)) if post_m else 0

    news_m = re.search(r'## 외부 뉴스.*?[(（](\d+)건', md_text)
    news_count = int(news_m.group(1)) if news_m else 0

    return pub_date, title, post_count, news_count


def inline_md(text):
    """인라인 마크다운 → HTML (링크·볼드·코드·이탤릭)."""
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    return text


def md_body_to_html(md_text):
    """draft md 본문 → HTML 블록 변환."""
    lines = md_text.split('\n')
    html = []
    in_front = False
    skip_sections = {'편집 메모'}   # HTML로 넣지 않을 섹션
    skip_active = False
    in_list = False

    for i, raw in enumerate(lines):
        line = raw.rstrip()

        # ── 프론트매터 스킵 ──
        if i == 0 and line.strip() == '---':
            in_front = True; continue
        if in_front:
            if line.strip() == '---': in_front = False
            continue

        # ── H1 스킵 (HTML <h1> 별도 배치) ──
        if line.startswith('# '):
            continue

        # ── blockquote ──
        if line.startswith('> '):
            if in_list: html.append('</ul>'); in_list = False
            html.append(f'<blockquote><p>{inline_md(line[2:].strip())}</p></blockquote>')
            continue

        # ── H2 ──
        if line.startswith('## '):
            if in_list: html.append('</ul>'); in_list = False
            sec = line[3:].strip()
            skip_active = any(s in sec for s in skip_sections)
            if not skip_active:
                html.append(f'<h2>{inline_md(sec)}</h2>')
            continue

        if skip_active:
            continue

        # ── H3 ──
        if line.startswith('### '):
            if in_list: html.append('</ul>'); in_list = False
            html.append(f'<h3>{inline_md(line[4:].strip())}</h3>')
            continue

        # ── 수평선 ──
        if line.strip() == '---':
            if in_list: html.append('</ul>'); in_list = False
            html.append('<hr>')
            continue

        # ── 리스트 ──
        if line.startswith('- '):
            if not in_list: html.append('<ul>'); in_list = True
            html.append(f'  <li>{inline_md(line[2:].strip())}</li>')
            continue

        # ── 빈 줄 ──
        if not line.strip():
            if in_list: html.append('</ul>'); in_list = False
            html.append('')
            continue

        # ── 일반 단락 ──
        if in_list: html.append('</ul>'); in_list = False
        html.append(f'<p>{inline_md(line.strip())}</p>')

    if in_list:
        html.append('</ul>')
    return '\n'.join(html)


# ─────────────────────────────────────────────
# HTML 생성
# ─────────────────────────────────────────────

def build_html(pub_date, title, post_count, news_count, body_html):
    y, mo, d = pub_date.split('-')
    date_kr = f"{y}년 {int(mo)}월 {int(d)}일"
    week_ago = (date.fromisoformat(pub_date) - timedelta(days=7)).isoformat()
    period = f"{week_ago} ~ {pub_date}"
    sa_summary = (
        f"{date_kr} 주간 브리핑. "
        f"이번 주 게시 {post_count}건, 외부 뉴스 {news_count}건 수집."
    )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · 철강 주재원</title>
<meta name="description" content="{sa_summary}">
<meta name="sa-title" content="{title}">
<meta name="sa-summary" content="{sa_summary}">
<meta name="sa-category" content="주간브리핑">
<meta name="sa-date" content="{pub_date}">
<meta name="sa-featured" content="false">
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
  <nav class="mh-nav"><a href="../index.html">홈</a><a href="../index.html#archive">아카이브</a></nav>
</div></header>

<main class="col">
<article>
  <a class="back" href="../index.html">← 홈으로</a>
  <div class="eyebrow">주간 브리핑 · 대상 기간 {period}</div>
  <h1 class="serif">{title}</h1>
  <div class="byline">철강 주재원 · {date_kr} · 편집실</div>

  <div class="article-body">
{body_html}
  </div>

  <div class="notes">
    <div class="meta">자동 수집 초안 — 편집실 검토 후 발행. 공개 자료 기반 (헌법 0조 부칙).</div>
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
# 메인
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="draft .md → HTML 브리핑 포스트 렌더")
    parser.add_argument('--date', default=date.today().isoformat(),
                        help='발행 날짜 YYYY-MM-DD (기본값: 오늘)')
    args = parser.parse_args()
    pub_date = args.date

    draft_path = SITE_DIR.parent / "drafts" / f"briefing-{pub_date}.md"
    if not draft_path.exists():
        print(f"❌ 초안 없음: {draft_path}")
        raise SystemExit(1)

    md_text = draft_path.read_text(encoding='utf-8')
    pub_date, title, post_count, news_count = parse_draft(md_text)
    body_html = md_body_to_html(md_text)
    html = build_html(pub_date, title, post_count, news_count, body_html)

    out_path = SITE_DIR / "posts" / f"briefing-{pub_date}.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding='utf-8')
    print(f"✅ HTML 렌더 완료: {out_path}")

    # build-index.py 실행 → posts.json 갱신
    build_index = SITE_DIR / "scripts" / "build-index.py"
    if build_index.exists():
        r = subprocess.run(["python3", str(build_index)], cwd=str(SITE_DIR),
                           capture_output=True, text=True)
        if r.returncode == 0:
            print("✅ posts.json 갱신 완료")
        else:
            print(f"⚠️ build-index 오류:\n{r.stderr}")
            raise SystemExit(1)
    else:
        print("⚠️ build-index.py 없음 — posts.json 미갱신")


if __name__ == "__main__":
    main()
