#!/usr/bin/env python3
"""
send_briefing_mail.py — 철강 주재원 브리핑 메일 발송

사용법:
  python3 send_briefing_mail.py

환경변수 (또는 .env 파일):
  GMAIL_USER         발신 Gmail 주소 (예: csband8@gmail.com)
  GMAIL_APP_PASSWORD Gmail 앱 비밀번호 (16자리)

구독자 목록: site/data/subscribers.json
최신 브리핑:  site/data/posts.json (featured=hero 항목)
"""

import json, os, smtplib, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from datetime import datetime

# ── 경로 설정 ─────────────────────────────────────────────────
BASE    = Path(__file__).parent.parent          # site/
DATA    = BASE / "data"
SUBS_F  = DATA / "subscribers.json"
POSTS_F = DATA / "posts.json"
SITE_URL = "https://goropak.github.io/steel-attache-site"

# ── 환경변수 ──────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent / ".env")
except ImportError:
    pass

GMAIL_USER = os.environ.get("GMAIL_USER", "csband8@gmail.com")
GMAIL_PASS = os.environ.get("GMAIL_APP_PASSWORD", "")

# ── 구독자 로드 ───────────────────────────────────────────────
def load_subscribers():
    if not SUBS_F.exists():
        print(f"[!] 구독자 파일 없음: {SUBS_F}")
        return []
    with open(SUBS_F, encoding="utf-8") as f:
        subs = json.load(f)
    return [s for s in subs if s.get("email")]

# ── 최신 브리핑 로드 ──────────────────────────────────────────
def load_latest_post():
    with open(POSTS_F, encoding="utf-8") as f:
        posts = json.load(f)
    # featured=hero 우선, 없으면 첫 번째
    for p in posts:
        if p.get("featured") == "hero":
            return p
    return posts[0] if posts else None

# ── HTML 이메일 본문 생성 ─────────────────────────────────────
def build_html(post, recipient_name=""):
    title   = post.get("title", "주간 브리핑")
    date    = post.get("date", datetime.today().strftime("%Y-%m-%d"))
    summary = post.get("summary", "")
    url     = SITE_URL + "/" + post.get("url", "")
    thumb   = SITE_URL + "/" + post.get("thumb", "") if post.get("thumb") else ""

    greeting = f"{recipient_name}님" if recipient_name else "안녕하세요"

    thumb_html = ""
    if thumb:
        thumb_html = f'<p style="margin:0 0 16px"><img src="{thumb}" alt="thumbnail" width="560" style="max-width:100%;border-radius:8px;display:block;"></p>'

    return f"""<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title></head>
<body style="margin:0;padding:0;background:#f5f3ee;font-family:system-ui,-apple-system,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f3ee;padding:32px 16px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

  <!-- 헤더 -->
  <tr><td style="background:#11161d;border-radius:10px 10px 0 0;padding:20px 28px;">
    <p style="margin:0;font-size:11px;letter-spacing:.08em;color:#9a8a7a;text-transform:uppercase;">철강 주재원 · Steel Attaché</p>
    <p style="margin:6px 0 0;font-size:18px;font-weight:700;color:#fff;line-height:1.3;">{title}</p>
    <p style="margin:6px 0 0;font-size:12px;color:#6b6459;">{date}</p>
  </td></tr>

  <!-- 본문 -->
  <tr><td style="background:#fff;padding:28px;">
    <p style="margin:0 0 16px;font-size:15px;color:#4a4a4a;">{greeting}, 이번 주 브리핑이 발행됐습니다.</p>

    {thumb_html}

    <p style="margin:0 0 20px;font-size:14px;color:#6b6459;line-height:1.7;">{summary}</p>

    <p style="margin:0;text-align:center;">
      <a href="{url}" style="display:inline-block;background:#D62828;color:#fff;text-decoration:none;
         padding:12px 28px;border-radius:99px;font-size:14px;font-weight:600;">
        전문 읽기 →
      </a>
    </p>
  </td></tr>

  <!-- 푸터 -->
  <tr><td style="background:#f5f3ee;border-radius:0 0 10px 10px;padding:16px 28px;text-align:center;">
    <p style="margin:0;font-size:11px;color:#9a8a7a;">
      포스코의 눈으로 읽는 세계 철강 분석 · 공개 자료 기반<br>
      구독 해지: <a href="mailto:csband8@gmail.com?subject=구독해지" style="color:#9a8a7a;">csband8@gmail.com</a>
    </p>
  </td></tr>

</table>
</td></tr>
</table>
</body></html>"""

# ── 발송 ─────────────────────────────────────────────────────
def send(post, subs, dry_run=False):
    if not GMAIL_PASS:
        print("[!] GMAIL_APP_PASSWORD 환경변수가 없습니다.")
        print("    ~/.zshrc 또는 .env 에 추가하세요:")
        print("    export GMAIL_APP_PASSWORD='xxxx xxxx xxxx xxxx'")
        sys.exit(1)

    title = post.get("title", "주간 브리핑")
    subject = f"[철강 주재원] {title}"

    ok = fail = 0
    for sub in subs:
        email = sub["email"]
        name  = sub.get("name", "")
        html  = build_html(post, name)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"철강 주재원 <{GMAIL_USER}>"
        msg["To"]      = email
        msg.attach(MIMEText(f"{title}\n\n{SITE_URL}/{post.get('url','')}", "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        if dry_run:
            print(f"[DRY] → {email}")
            ok += 1
            continue

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
                s.login(GMAIL_USER, GMAIL_PASS)
                s.sendmail(GMAIL_USER, email, msg.as_string())
            print(f"[OK] → {email}")
            ok += 1
        except Exception as e:
            print(f"[FAIL] {email}: {e}")
            fail += 1

    print(f"\n완료: 성공 {ok} / 실패 {fail} / 전체 {ok+fail}")

# ── 메인 ─────────────────────────────────────────────────────
if __name__ == "__main__":
    dry = "--dry" in sys.argv

    subs = load_subscribers()
    if not subs:
        print("[!] 구독자가 없습니다. admin.html에서 추가 후 subscribers.json을 저장하세요.")
        sys.exit(0)

    post = load_latest_post()
    if not post:
        print("[!] posts.json이 비어 있습니다.")
        sys.exit(1)

    print(f"브리핑: {post.get('title')}")
    print(f"구독자: {len(subs)}명{'  [DRY RUN]' if dry else ''}")
    print("-" * 40)
    send(post, subs, dry_run=dry)
