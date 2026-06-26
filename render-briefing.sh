#!/bin/bash
# render-briefing.sh — 브리핑 초안 렌더 + 커밋 + push
# 사용: bash render-briefing.sh YYYY-MM-DD
# approval_gate.py 승인 시 자동 호출됨 (ALLOWED: ["bash","render-briefing.sh"])
set -e

cd "$(dirname "$0")"   # site/ 디렉토리 기준으로 고정

DATE="${1:-$(date +%Y-%m-%d)}"
echo "=== 주간브리핑 렌더 파이프라인: ${DATE} ==="

# 1) unstaged 변경이 있으면 stash 후 pull, 이후 복원
echo "→ git pull..."
STASHED=0
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "  ⚠️ unstaged/staged 변경 감지 — stash 임시 보관"
    git stash push -u -m "render-briefing auto-stash ${DATE}"
    STASHED=1
fi
git pull --rebase origin main
if [ "${STASHED}" = "1" ]; then
    echo "  → stash 복원"
    git stash pop
fi

# 2) draft → HTML 렌더 + posts.json 갱신
echo "→ HTML 렌더 중..."
python3 scripts/render-briefing.py --date "${DATE}"

# 3) 변경 파일 스테이징
git add "posts/briefing-${DATE}.html" data/posts.json

# 4) 커밋 (변경 없으면 스킵)
if git diff --cached --quiet; then
    echo "⚠️ 변경 없음 — 커밋 건너뜀"
else
    git commit -m "auto: 주간브리핑 ${DATE} 발행 (telegram-gate 승인)"
    echo "✅ 커밋 완료"
fi

# 5) push
echo "→ push..."
git push origin main

echo "=== 완료: 주간브리핑 ${DATE} GitHub Pages 반영 ==="

# 6) 구독자 메일 발송
echo "→ 구독자 메일 발송 중..."
python3 scripts/send_briefing_mail.py && echo "✅ 메일 발송 완료" || echo "⚠️ 메일 발송 실패 (수동 실행: python3 scripts/send_briefing_mail.py)"
