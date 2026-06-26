#!/usr/bin/env python3
"""weekly-briefing.py v2 — posts.json + RSS 폴링 기반 주간 브리핑 초안 생성.
사용: python3 scripts/weekly-briefing.py  (site/ 루트에서 실행)
출력: steel-attache/drafts/briefing-{날짜}.md
"""

import json
import logging
import os
import sys
from datetime import date, timedelta
from pathlib import Path

# scripts/ 폴더 경로 추가 — rss_sources 모듈 import용
sys.path.insert(0, os.path.dirname(__file__))

try:
    import feedparser
    logging.getLogger("feedparser").setLevel(logging.ERROR)
except ImportError:
    feedparser = None

from rss_sources import BACKBONE_FEEDS, GNEWS_QUERIES

POSTS_JSON = Path("data/posts.json")
DRAFTS = Path("../drafts")


def fetch_rss_news(days=7):
    """백본 + 우회 RSS에서 최근 N일 뉴스 수집."""
    if feedparser is None:
        print("  ⚠️ feedparser 없음 — RSS 수집 건너뜀 (pip3 install feedparser)")
        return []

    results = []

    # 백본 계층
    for src in BACKBONE_FEEDS:
        try:
            feed = feedparser.parse(src["url"])
            count = 0
            for entry in feed.entries:
                if src["filter_tags"]:
                    tags = [t.term for t in getattr(entry, "tags", [])]
                    if not any(f in tags for f in src["filter_tags"]):
                        continue
                results.append({
                    "source": src["name"],
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "date": entry.get("published", "")[:10],
                })
                count += 1
            print(f"  ✅ {src['name']}: {count}건")
        except Exception as e:
            print(f"  ❌ {src['name']} 오류: {e}")

    # 우회 계층 (0건 경고 로그 필수)
    for src in GNEWS_QUERIES:
        try:
            feed = feedparser.parse(src["url"])
            count = len(feed.entries)
            if count == 0:
                print(f"  ⚠️ 경고: {src['name']} 결과 0건 — 피드 확인 필요")
            else:
                for entry in feed.entries[:5]:
                    results.append({
                        "source": src["name"],
                        "title": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "date": entry.get("published", "")[:10],
                    })
                print(f"  ✅ {src['name']}: {min(count, 5)}건")
        except Exception as e:
            print(f"  ❌ {src['name']} 오류: {e}")

    return results


def main():
    DRAFTS.mkdir(parents=True, exist_ok=True)
    today = date.today()
    week_ago = today - timedelta(days=7)

    posts = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    recent_posts = [p for p in posts if p.get("date", "") >= week_ago.isoformat()]

    print("RSS 폴링 중...")
    news_items = fetch_rss_news(days=7)

    lines = [
        "---",
        f"작성일: {today.isoformat()}",
        "상태: 초안 — 사람 검토 후 발행",
        "---",
        "",
        f"# 주간 브리핑 — {today.strftime('%Y년 %m월 %d일')}",
        "",
        "> 이 초안은 자동 생성되었습니다. 발행 전 반드시 사람이 검토합니다.",
        "",
        f"## 이번 주 게시 ({len(recent_posts)}건)",
        "",
    ]
    for p in sorted(recent_posts, key=lambda x: x["date"], reverse=True):
        lines += [
            f"### [{p['title']}]({p['url']})",
            f"**{p['date']}** | {p['category']}",
            "",
            p["summary"],
            "",
        ]

    lines += ["---", f"## 외부 뉴스 ({len(news_items)}건 수집)", ""]
    if news_items:
        for item in news_items[:20]:
            lines.append(f"- [{item['title']}]({item['url']}) `{item['source']}` {item['date']}")
    else:
        lines.append("_수집된 뉴스 없음_")
    lines.append("")

    lines += [
        "---",
        "## 편집 메모 (사람이 작성)",
        "",
        "<!-- 이번 주 핵심 인사이트, 포스코 시사점 등 추가 -->",
        "",
    ]

    out = DRAFTS / f"briefing-{today.isoformat()}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n→ 초안 생성: {out}")
    print("  검토 후: python3 scripts/publish-request.py briefing-{날짜} \"주간 브리핑 {날짜}\"")


if __name__ == "__main__":
    main()
