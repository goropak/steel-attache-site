#!/bin/bash
# 아티클 네비게이션 배포 스크립트
set -e
SITE="/Users/clean/Desktop/project/steel-attache/site"

find "$SITE/.git" -name "*.lock" -delete 2>/dev/null || true

cd "$SITE"
git add js/article.js style.css \
  posts/japan-steel-01.html posts/japan-steel-02.html \
  posts/japan-steel-03.html posts/japan-steel-04.html \
  posts/japan-steel-05.html posts/japan-steel-06.html

git commit -m "feat: 아티클 네비게이션 — 시리즈 도트·고정 바·이전다음 카드"
git push origin main
echo "✅ 배포 완료"
