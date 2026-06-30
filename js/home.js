/* home.js — 포털 홈 피처드·최신 그리드 렌더 (steel-attache B3) */
(function () {
  function metaHtml(p) {
    return '<div class="card-meta"><span>' + p.date + '</span><span>' + p.category + '</span></div>';
  }

  var CAT_COLORS = {
    '숲': '#4a7c59',
    '일본': '#8b4513',
    '중국': '#8B0000',
    '미국': '#1a4a8a',
    '유럽': '#1a3a6a',
    '인도': '#7a4000',
    '주간브리핑': '#2c3e50',
    '철강': '#374151'
  };

  function thumbHtml(p) {
    if (p.thumb) {
      return '<div class="card-thumb"><img src="' + p.thumb + '" alt="' + p.title +
        '" loading="lazy" width="640" height="360"></div>';
    }
    var bg = CAT_COLORS[p.category] || '#4a5568';
    return '<div class="card-thumb" style="background:linear-gradient(135deg,' +
      bg + '18,' + bg + '36);display:flex;align-items:center;justify-content:center;">' +
      catSvg(p.category, bg) + '</div>';
  }

  function catSvg(cat, color) {
    if (cat === '숲' || cat === '철강') {
      return '<svg width="48" height="48" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
        '<path d="M20 6 L32 30 H8 Z" fill="none" stroke="' + color + '" stroke-width="2" stroke-linejoin="round" opacity="0.5"/>' +
        '<path d="M20 17 L28 30 H12 Z" fill="' + color + '" opacity="0.35"/>' +
        '</svg>';
    }
    if (cat === '주간브리핑') {
      return '<svg width="48" height="48" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
        '<rect x="6" y="8" width="28" height="24" rx="3" stroke="' + color + '" stroke-width="1.5" opacity="0.45"/>' +
        '<path d="M11 16 H29 M11 21 H25 M11 26 H22" stroke="' + color + '" stroke-width="1.5" stroke-linecap="round" opacity="0.45"/>' +
        '</svg>';
    }
    return '<svg width="48" height="48" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
      '<circle cx="20" cy="20" r="12" stroke="' + color + '" stroke-width="1.5" opacity="0.4"/>' +
      '<path d="M8 20 Q14 14 20 20 Q26 26 32 20" stroke="' + color + '" stroke-width="1.5" fill="none" opacity="0.4"/>' +
      '</svg>';
  }

  function heroCard(p) {
    return '<a class="feat-hero-card is-hero" href="' + p.url + '">' +
      thumbHtml(p) +
      '<div class="card-body">' +
        '<div class="card-cat">' + p.category + '</div>' +
        '<h3>' + p.title + '</h3>' +
        (p.summary ? '<div class="card-summary">' + p.summary + '</div>' : '') +
        metaHtml(p) +
      '</div>' +
      '</a>';
  }

  function sideCard(p) {
    return '<a class="side-card" href="' + p.url + '">' +
      '<div class="card-cat">' + p.category + '</div>' +
      '<h4>' + p.title + '</h4>' +
      metaHtml(p) +
      '</a>';
  }

  function latestCard(p) {
    return '<a class="latest-card" href="' + p.url + '">' +
      '<div class="lc-cat">' + p.category + '</div>' +
      '<div class="lc-title">' + p.title + '</div>' +
      (p.summary ? '<div class="lc-summary">' + p.summary + '</div>' : '') +
      metaHtml(p) +
      '</a>';
  }

  /* 글 HTML에서 첫 번째 <figure class="infog"> SVG를 추출해 thumb div에 주입 */
  function injectInfogThumb(articleUrl, thumbDiv) {
    fetch(articleUrl)
      .then(function (r) { return r.text(); })
      .then(function (html) {
        var parser = new DOMParser();
        var doc = parser.parseFromString(html, 'text/html');
        var fig = doc.querySelector('figure.infog');
        if (fig) {
          var svg = fig.querySelector('svg');
          if (svg) {
            thumbDiv.style.background = '#f5f3ee';
            thumbDiv.style.padding = '0';
            thumbDiv.style.display = 'block';
            thumbDiv.style.overflow = 'hidden';
            thumbDiv.innerHTML = svg.outerHTML;
            var injected = thumbDiv.querySelector('svg');
            if (injected) {
              /* 16:9 컨테이너를 꽉 채우도록 — object-fit:cover 효과 */
              injected.setAttribute('preserveAspectRatio', 'xMidYMid slice');
              injected.style.cssText = 'width:100%;height:100%;display:block;position:absolute;top:0;left:0;';
              thumbDiv.style.position = 'relative';
            }
          }
        }
      })
      .catch(function () {});
  }

  function init() {
    fetch('data/posts.json')
      .then(function (r) { return r.json(); })
      .then(function (posts) {
        /* posts.json 맨 위 = 가장 최신 글 → 항상 히어로 */
        var hero = posts[0];

        var sides = posts.filter(function (p) { return p !== hero; }).slice(0, 4);
        var left = sides.slice(0, 2);
        var right = sides.slice(2, 4);

        var heroEl = document.getElementById('feat-hero');
        var leftEl = document.getElementById('feat-left');
        var rightEl = document.getElementById('feat-right');
        var latestEl = document.getElementById('latest-grid');

        if (heroEl && hero) {
          heroEl.innerHTML = heroCard(hero);
          /* thumb이 없으면 글의 첫 인포그래픽 SVG를 가져와 채운다 */
          if (!hero.thumb) {
            var thumbDiv = heroEl.querySelector('.card-thumb');
            if (thumbDiv) injectInfogThumb(hero.url, thumbDiv);
          }
        }
        if (leftEl) leftEl.innerHTML = left.map(sideCard).join('');
        if (rightEl) rightEl.innerHTML = right.map(sideCard).join('');
        if (latestEl) latestEl.innerHTML = posts.map(latestCard).join('');
      })
      .catch(function () {});
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
