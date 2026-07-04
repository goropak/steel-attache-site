#!/usr/bin/env python3
"""
send_briefing_mail.py — 철강 주재원 브리핑 메일 발송

사용법:
  python3 send_briefing_mail.py          # 실제 발송
  python3 send_briefing_mail.py --dry    # 테스트 (발송 안 함)

환경변수:
  GMAIL_USER         발신 Gmail 주소
  GMAIL_APP_PASSWORD Gmail 앱 비밀번호 (16자리)
"""

import json, os, re, smtplib, sys
from email.message import EmailMessage
from email import policy as email_policy
from pathlib import Path
from datetime import datetime
from html.parser import HTMLParser

BASE     = Path(__file__).parent.parent
DATA     = BASE / "data"
POSTS_F  = DATA / "posts.json"
SUBS_F   = DATA / "subscribers.json"
POSTS_DIR = BASE / "posts"
SITE_URL  = "https://goropak.github.io/steel-attache-site"

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent / ".env")
except ImportError:
    pass

GMAIL_USER = os.environ.get("GMAIL_USER", "csband8@gmail.com")
GMAIL_PASS = os.environ.get("GMAIL_APP_PASSWORD", "").replace('\xa0', '').replace(' ', '')

# ── HTML 파싱 — 본문 섹션 추출 ────────────────────────────────
class BriefingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_h2 = self.in_p = self.in_blockquote = self.in_lead = False
        self.h2s, self.leads, self.blockquotes = [], [], []
        self._buf = ""
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class","")
        if tag == "h2": self.in_h2 = True
        if tag == "p" and "lead" in cls: self.in_lead = True
        if tag == "blockquote": self.in_blockquote = True; self._depth += 1
        if tag == "p" and self.in_blockquote: self.in_p = True

    def handle_endtag(self, tag):
        if tag == "h2":
            if self._buf.strip(): self.h2s.append(self._buf.strip())
            self._buf = ""; self.in_h2 = False
        if tag == "p" and self.in_lead:
            if self._buf.strip(): self.leads.append(self._buf.strip())
            self._buf = ""; self.in_lead = False
        if tag == "p" and self.in_blockquote:
            if self._buf.strip(): self.blockquotes.append(self._buf.strip())
            self._buf = ""; self.in_p = False
        if tag == "blockquote":
            self._depth -= 1
            if self._depth == 0: self.in_blockquote = False

    def handle_data(self, data):
        if self.in_h2 or self.in_lead or (self.in_blockquote and self.in_p):
            self._buf += data

def parse_briefing(html_path):
    text = html_path.read_text(encoding="utf-8")
    p = BriefingParser()
    p.feed(text)
    # meta description
    desc_m = re.search(r'<meta name="sa-summary" content="([^"]+)"', text)
    desc = desc_m.group(1) if desc_m else ""
    return {"h2s": p.h2s, "leads": p.leads, "blockquotes": p.blockquotes, "summary": desc}

# ── 이메일 HTML 생성 ──────────────────────────────────────────
def clean(s):
    """비ASCII 공백 등 문제 문자 제거"""
    return s.replace('\xa0', ' ').replace('​', '').strip()

def build_html(post, content, recipient_name="", recipient_email=""):
    title    = post.get("title","주간 브리핑")
    date     = post.get("date", datetime.today().strftime("%Y-%m-%d"))
    post_url = SITE_URL + "/" + post.get("url","")
    thumb    = SITE_URL + "/" + post.get("thumb","") if post.get("thumb") else ""
    greeting = f"{recipient_name}님" if recipient_name else "안녕하세요"

    # 리드 문장 (최대 2개)
    leads_html = ""
    for l in content["leads"][:2]:
        leads_html += f'<p style="margin:0 0 12px;font-size:15px;color:#2c2c2c;line-height:1.75;">{clean(l)}</p>'

    # 섹션 카드 (h2 + blockquote 쌍)
    sections_html = ""
    h2s = content["h2s"]
    bqs = content["blockquotes"]
    for i, h2 in enumerate(h2s[:2]):
        bq = bqs[i] if i < len(bqs) else ""
        # 한국 관점 강조
        bq_html = ""
        if bq:
            bq_clean = clean(re.sub(r'<[^>]+>', '', bq))
            bq_html = f"""
            <div style="border-left:3px solid #D62828;padding:10px 14px;background:#fff8f8;border-radius:0 6px 6px 0;margin-top:10px;">
              <p style="margin:0;font-size:13px;color:#4a4a4a;line-height:1.65;">{bq_clean}</p>
            </div>"""
        sections_html += f"""
        <div style="background:#f9f7f4;border-radius:8px;padding:16px 18px;margin-bottom:14px;">
          <p style="margin:0 0 8px;font-size:13px;font-weight:700;color:#11161d;">{h2}</p>
          {bq_html}
        </div>"""

    # 썸네일
    thumb_html = ""
    if thumb:
        thumb_html = f'<img src="{thumb}" alt="브리핑 인포그래픽" width="560" style="width:100%;max-width:560px;display:block;border-radius:8px;margin:0 0 20px;">'

    return f"""<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title></head>
<body style="margin:0;padding:0;background:#f0ede8;font-family:'Apple SD Gothic Neo',system-ui,-apple-system,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0ede8;padding:28px 12px;">
<tr><td align="center">
<table width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%;">

  <!-- 헤더 -->
  <tr><td style="background:#11161d;border-radius:12px 12px 0 0;padding:22px 28px 18px;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td>
          <p style="margin:0 0 2px;font-size:10px;letter-spacing:.1em;color:#9a8a7a;text-transform:uppercase;">철강 주재원 · Steel Attaché</p>
          <p style="margin:0 0 2px;font-size:20px;font-weight:700;color:#fff;line-height:1.3;">{title}</p>
          <p style="margin:0;font-size:12px;color:#6b6459;">주간 브리핑 · {date}</p>
        </td>
        <td align="right" style="width:48px;">
          <div style="width:36px;height:36px;background:#D62828;border-radius:8px;display:inline-block;
            line-height:36px;text-align:center;font-size:18px;font-weight:900;color:#fff;">鐵</div>
        </td>
      </tr>
    </table>
  </td></tr>

  <!-- 빨간 라인 -->
  <tr><td style="background:#D62828;height:3px;"></td></tr>

  <!-- 본문 -->
  <tr><td style="background:#fff;padding:28px 28px 20px;">

    <p style="margin:0 0 18px;font-size:14px;color:#6b6459;">{greeting}, 이번 주 철강 주재원 브리핑입니다.</p>

    {thumb_html}

    {leads_html}

    <!-- 핵심 섹션 -->
    <p style="margin:0 0 10px;font-size:11px;font-weight:700;letter-spacing:.08em;color:#9a8a7a;text-transform:uppercase;">이번 주 핵심</p>
    {sections_html}

    <!-- CTA -->
    <div style="text-align:center;margin:24px 0 8px;">
      <a href="{post_url}"
         style="display:inline-block;background:#D62828;color:#fff;text-decoration:none;
                padding:13px 32px;border-radius:99px;font-size:14px;font-weight:700;
                letter-spacing:.02em;">
        전문 읽기 →
      </a>
    </div>

  </td></tr>

  <!-- 푸터 -->
  <tr><td style="background:#f9f7f4;border-radius:0 0 12px 12px;padding:16px 28px;border-top:1px solid #e6e0d4;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td style="font-size:11px;color:#9a8a7a;line-height:1.6;">
          포스코의 눈으로 읽는 세계 철강 분석<br>
          공개 자료 기반, 출처 명기
        </td>
        <td align="right" style="font-size:11px;color:#c8c0b4;">
          <a href="{SITE_URL}/unsubscribe.html?email={recipient_email}" style="color:#c8c0b4;text-decoration:underline;">구독 해지</a>
        </td>
      </tr>
    </table>
  </td></tr>

</table>
</td></tr>
</table>
</body></html>"""

# ── 구독자 / 포스트 로드 ──────────────────────────────────────
def load_subscribers():
    if not SUBS_F.exists():
        print(f"[!] 구독자 파일 없음: {SUBS_F}")
        return []
    with open(SUBS_F, encoding="utf-8") as f:
        return [s for s in json.load(f) if s.get("email")]

def load_latest_post():
    with open(POSTS_F, encoding="utf-8") as f:
        posts = json.load(f)
    if not posts:
        return None
    # hero 중 최신 날짜 우선, 없으면 전체 중 최신 날짜 (배열 순서에 의존하지 않음)
    heroes = [p for p in posts if p.get("featured") == "hero"]
    pool = heroes or posts
    return max(pool, key=lambda p: p.get("date", ""))

# ── 발송 ─────────────────────────────────────────────────────
def send(post, content, subs, dry_run=False):
    if not GMAIL_PASS and not dry_run:
        print("[!] GMAIL_APP_PASSWORD 환경변수를 설정해 주세요.")
        print("    export GMAIL_APP_PASSWORD='xxxx xxxx xxxx xxxx'")
        sys.exit(1)

    title   = post.get("title","주간 브리핑")
    subject = f"[철강 주재원] {title}"
    ok = fail = 0

    for sub in subs:
        email = sub["email"]
        name  = sub.get("name","")
        html  = build_html(post, content, name, email)
        plain = f"{title}\n{SITE_URL}/{post.get('url','')}\n\n구독 해지: csband8@gmail.com"

        # \xa0 등 비ASCII 공백 전체 제거
        html  = html.replace('\xa0', ' ')
        plain = plain.replace('\xa0', ' ')

        msg = EmailMessage(policy=email_policy.SMTP)
        msg["Subject"] = subject
        msg["From"]    = f"Steel Attache <{GMAIL_USER}>"
        msg["To"]      = email
        msg.set_content(plain, charset="utf-8")
        msg.add_alternative(html, subtype="html", charset="utf-8")

        if dry_run:
            print(f"[DRY] → {email}")
            ok += 1
            continue
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
                s.login(GMAIL_USER, GMAIL_PASS)
                s.send_message(msg)
            print(f"[OK]  → {email}")
            ok += 1
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[FAIL] {email}: {e}")
            fail += 1

    print(f"\n완료: 성공 {ok} / 실패 {fail} / 전체 {ok+fail}")

# ── 특정 포스트 검색 ──────────────────────────────────────────
def find_post_by_url(url_fragment):
    """URL 일부로 포스트를 찾는다. 예: 'china-tech-01' 또는 'posts/china-tech-01.html'"""
    with open(POSTS_F, encoding="utf-8") as f:
        posts = json.load(f)
    for p in posts:
        if url_fragment in p.get("url", ""):
            return p
    return None

# ── 메인 ─────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="철강 주재원 구독자 메일 발송")
    parser.add_argument("--dry", action="store_true", help="발송 안 함 (테스트)")
    parser.add_argument("--post", type=str, default=None,
                        help="특정 포스트 지정 (예: china-tech-01 또는 posts/china-tech-01.html)")
    args = parser.parse_args()
    dry = args.dry

    subs = load_subscribers()
    if not subs:
        print("[!] 구독자가 없습니다. admin.html에서 추가 후 site/data/subscribers.json을 저장하세요.")
        sys.exit(0)

    if args.post:
        post = find_post_by_url(args.post)
        if not post:
            print(f"[!] '{args.post}'에 해당하는 포스트를 posts.json에서 찾을 수 없습니다.")
            print("    등록된 포스트 목록:")
            with open(POSTS_F, encoding="utf-8") as f:
                for p in json.load(f):
                    print(f"      {p.get('url','')}  ←  {p.get('title','')[:40]}")
            sys.exit(1)
        print(f"[지정 포스트] {post.get('title')}")
    else:
        post = load_latest_post()

    if not post:
        print("[!] posts.json이 비어 있습니다.")
        sys.exit(1)

    # HTML 파싱
    post_path = POSTS_DIR / Path(post.get("url","")).name
    content = {"h2s":[], "leads":[], "blockquotes":[], "summary": post.get("summary","")}
    if post_path.exists():
        content = parse_briefing(post_path)

    print(f"포스트: {post.get('title')}")
    print(f"구독자: {len(subs)}명{'  [DRY RUN]' if dry else ''}")
    print("-" * 40)
    send(post, content, subs, dry_run=dry)
