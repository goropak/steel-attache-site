/* list.js — 카테고리 필터 목록 (steel-attache B3) */
(function () {
  function init() {
    var params = new URLSearchParams(location.search);
    var cat = params.get('cat') || '';

    var titleEl = document.getElementById('list-title');
    var countEl = document.getElementById('list-count');
    var container = document.getElementById('post-list');
    if (!container) return;

    if (titleEl) titleEl.textContent = cat || '전체 글';

    fetch('data/posts.json')
      .then(function (r) { return r.json(); })
      .then(function (posts) {
        var filtered = cat ? posts.filter(function (p) { return p.category === cat; }) : posts;
        if (countEl) countEl.textContent = filtered.length + '건';

        if (!filtered.length) {
          container.innerHTML = '<p class="list-empty">해당 카테고리의 글이 아직 없습니다.</p>';
          return;
        }

        container.innerHTML = filtered.map(function (p, i) {
          var num = String(filtered.length - i).padStart(2, '0');
          return '<a class="post-list-item" href="' + p.url + '">' +
            '<div class="pli-num">' + num + '</div>' +
            '<div class="pli-body">' +
              '<div class="pli-cat">' + p.category + '</div>' +
              '<div class="pli-title">' + p.title + '</div>' +
              (p.summary ? '<div class="pli-summary">' + p.summary + '</div>' : '') +
              '<div class="pli-meta">' + p.date + '</div>' +
            '</div>' +
            '</a>';
        }).join('');
      })
      .catch(function () {
        container.innerHTML = '<p class="list-empty">글 목록을 불러오지 못했습니다. HTTP 서버에서 열어주세요.</p>';
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
