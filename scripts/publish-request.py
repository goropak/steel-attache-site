#!/usr/bin/env python3
"""publish-request.py — 발행 게이트 요청서 자동 생성.
사용: python3 scripts/publish-request.py <slug> "<제목>"
예:  python3 scripts/publish-request.py china-01 "10억 톤의 나라 — 중국편"
"""

import sys
import subprocess
from datetime import date
from pathlib import Path

APPROVALS = Path("../../governance/approvals")
SITE_PATH = "~/Desktop/project/steel-attache/site"

def main():
    if len(sys.argv) < 3:
        print("사용: python3 scripts/publish-request.py <slug> <제목>")
        sys.exit(1)

    slug = sys.argv[1]
    title = sys.argv[2]
    today = date.today().isoformat()
    fname = APPROVALS / f"{today}-publish-{slug}.md"

    # build-index 먼저 실행
    result = subprocess.run(
        [sys.executable, "scripts/build-index.py"],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        print("❌ build-index 실패 — 중단")
        sys.exit(1)

    # git diff 확인
    diff = subprocess.run(
        ["git", "diff", "--stat"],
        capture_output=True, text=True
    ).stdout.strip()

    # telegram-gate 형식: 대상 cwd, bare git 명령 (git -C / && / ; 금지)
    content = f"""무엇: steel-attache 글 발행 — {title}
왜: 사람 검토 완료, 발행 승인 요청.
대상: {SITE_PATH}
변경 요약:
{diff or "  (변경 없음 — 이미 커밋됨)"}
명령:
- git add -A
- git commit -m "content: {slug} — {title}"
- git push origin main
"""
    APPROVALS.mkdir(parents=True, exist_ok=True)
    fname.write_text(content, encoding="utf-8")
    print(f"→ 요청서 생성: {fname}")
    print("  telegram-gate가 폴링하면 텔레그램으로 승인 알림 전송됩니다.")

if __name__ == "__main__":
    main()
