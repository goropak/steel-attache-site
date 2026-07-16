#!/usr/bin/env python3
"""build-index.py — posts/*.html sa-* 메타 태그 → data/posts.json 자동 생성.
사용: python scripts/build-index.py (site/ 루트에서 실행)
"""

import json
import re
from pathlib import Path

POSTS_DIR = Path("posts")
PREMIUM_DIR = Path("premium")  # 유료(승인제) 글 — 암호화 게이트. 본문은 암호문, 목록엔 티저만.
OUT = Path("data/posts.json")

def parse_meta(html: str, name: str) -> str:
    m = re.search(rf'<meta\s+name="sa-{name}"\s+content="([^"]*)"', html)
    return m.group(1).strip() if m else ""

def collect(dir_path: Path, url_prefix: str, posts: list):
    if not dir_path.exists():
        return
    for p in sorted(dir_path.glob("*.html"), reverse=True):
        html = p.read_text(encoding="utf-8")
        if 'name="sa-title"' not in html:
            print(f"  건너뜀 (sa-* 없음): {url_prefix}{p.name}")
            continue
        entry = {
            "title":    parse_meta(html, "title"),
            "summary":  parse_meta(html, "summary"),
            "category": parse_meta(html, "category"),
            "author":   parse_meta(html, "author") or "편집실",
            "date":     parse_meta(html, "date"),
            "url":      f"{url_prefix}{p.name}",
            "thumb":    parse_meta(html, "thumb"),
            "featured": parse_meta(html, "featured"),
            "premium":  parse_meta(html, "premium"),  # "true"면 유료(암호화 게이트) 글
        }
        posts.append(entry)
        print(f"  ✅ {url_prefix}{p.name}: {entry['title'][:30]}")

def build():
    posts = []
    collect(POSTS_DIR, "posts/", posts)
    collect(PREMIUM_DIR, "premium/", posts)

    # 날짜 내림차순 정렬 (featured=hero 최상단 고정)
    posts.sort(key=lambda x: x["date"], reverse=True)
    posts.sort(key=lambda x: x["featured"] != "hero")  # stable — hero만 최상단으로

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n→ {OUT} 생성 완료 ({len(posts)}건)")

if __name__ == "__main__":
    build()
