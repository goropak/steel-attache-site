#!/usr/bin/env python3
"""weekly-briefing.py — posts.json 기반 주간 브리핑 초안 생성 (발행 전 사람 검토 필수).
사용: python3 scripts/weekly-briefing.py
출력: steel-attache/drafts/briefing-{오늘날짜}.md (초안, 자동공개 없음)
"""

import json
from datetime import date, timedelta
from pathlib import Path

POSTS_JSON = Path("data/posts.json")
DRAFTS = Path("../drafts")

def main():
    DRAFTS.mkdir(parents=True, exist_ok=True)
    today = date.today()
    week_ago = today - timedelta(days=7)

    posts = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    recent = [
        p for p in posts
        if p.get("date", "") >= week_ago.isoformat()
    ]

    lines = [
        f"---",
        f"작성일: {today.isoformat()}",
        f"상태: 초안 — 사람 검토 후 발행",
        f"---",
        f"",
        f"# 주간 브리핑 — {today.strftime('%Y년 %m월 %d일')}",
        f"",
        f"> 이 초안은 자동 생성되었습니다. 발행 전 반드시 사람이 검토합니다.",
        f"",
        f"## 이번 주 게시 ({len(recent)}건)",
        "",
    ]
    for p in sorted(recent, key=lambda x: x["date"], reverse=True):
        lines.append(f"### [{p['title']}]({p['url']})")
        lines.append(f"**{p['date']}** | {p['category']}")
        lines.append(f"")
        lines.append(f"{p['summary']}")
        lines.append(f"")

    lines += [
        "---",
        "## 편집 메모 (사람이 작성)",
        "",
        "<!-- 이번 주 핵심 인사이트, 포스코 시사점 등 추가 -->",
        "",
    ]

    out = DRAFTS / f"briefing-{today.isoformat()}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"→ 초안 생성: {out}")
    print("  검토 후 발행 시: python3 scripts/publish-request.py briefing-{날짜} \"주간 브리핑 {날짜}\"")

if __name__ == "__main__":
    main()
