#!/bin/bash
set -e
SITE="$(cd "$(dirname "$0")" && pwd)"
find "$SITE/.git" -name "*.lock" -delete 2>/dev/null || true
git -C "$SITE" commit -am "feat: JSONBin 연동 — 질문 즉시 자동 게시"
git -C "$SITE" push origin main
echo "완료"
