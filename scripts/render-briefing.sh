#!/bin/bash
# 주간 브리핑 렌더 + 게시 + 구독자 메일 발송 (통합 스크립트, #2026-07-18-SA-MAILFIX §1 복원)
# 사용: bash render-briefing.sh <YYYY-MM-DD>   (인자 생략 시 오늘 날짜)
# 텔레그램 게이트 화이트리스트가 ["bash","render-briefing.sh"] 토큰 2개까지만 매칭하므로
# 뒤따르는 날짜 인자는 그대로 통과한다 — 렌더→색인→커밋→push→메일 전 체인이 반드시
# 이 스크립트 내부에서 처리돼야 한다(게이트 FORBIDDEN이 호출부의 && 체이닝을 막음).
set -e
SITE="$(cd "$(dirname "$0")/.." && pwd)"
DATE="${1:-$(date +%Y-%m-%d)}"

echo "[render-briefing] lock 정리..."
rm -f "$SITE/.git/index.lock"

echo "[render-briefing] 렌더 (+ build-index.py는 render-briefing.py 내부에서 자동 호출됨)..."
python3 "$SITE/scripts/render-briefing.py" --date "$DATE"

echo "[render-briefing] commit..."
git -C "$SITE" add -A
git -C "$SITE" commit -m "brief: ${DATE} 주간 브리핑 발행"

echo "[render-briefing] push..."
git -C "$SITE" push origin main

echo "[render-briefing] 구독자 메일 발송..."
python3 "$SITE/scripts/send_briefing_mail.py" --post "briefing-${DATE}"

echo "[render-briefing] 완료"
