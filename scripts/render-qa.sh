#!/bin/bash
# Q&A JSONBin 연동 배포 스크립트
set -e
SITE="$(cd "$(dirname "$0")/.." && pwd)"

echo "[render-qa] lock 정리..."
rm -f "$SITE/.git/index.lock"

echo "[render-qa] commit..."
git -C "$SITE" commit -am "feat: JSONBin 연동 — 질문 즉시 자동 게시"

echo "[render-qa] push..."
git -C "$SITE" push origin main

echo "[render-qa] 완료"
