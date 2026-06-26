#!/bin/bash
# render-qa.sh — Q&A 초안 렌더 + 커밋 + push
# 사용: bash render-qa.sh qa-001
# approval_gate.py 승인 시 자동 호출됨 (ALLOWED: ["bash","render-qa.sh"])
set -e

cd "$(dirname "$0")"   # site/ 디렉토리 기준으로 고정

ID="${1:?ID 필요 (예: qa-001)}"
echo "=== Q&A 렌더 파이프라인: ${ID} ==="

# 1) 최신 코드 pull
echo "→ git pull..."
git pull --rebase origin main

# 2) draft → HTML 렌더 + questions.json 갱신
echo "→ HTML 렌더 중..."
python3 scripts/render-qa.py --id "${ID}"

# 3) 변경 파일 스테이징
git add "qa/${ID}.html" data/questions.json

# 4) 커밋 (변경 없으면 스킵)
if git diff --cached --quiet; then
    echo "⚠️ 변경 없음 — 커밋 건너뜀"
else
    git commit -m "auto: Q&A ${ID} 발행 (telegram-gate 승인)"
    echo "✅ 커밋 완료"
fi

# 5) push
echo "→ push..."
git push origin main

echo "=== 완료: Q&A ${ID} GitHub Pages 반영 ==="
