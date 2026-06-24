/* search.js — 한글 부분일치 + 초성 + 다중 AND (steel-attache B3) */
(function () {
  var posts = [];

  var INITIALS = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'];

  function getInitial(ch) {
    var code = ch.charCodeAt(0);
    if (code >= 0xAC00 && code <= 0xD7A3) {
      return INITIALS[Math.floor((code - 0xAC00) / 28 / 21)];
    }
    return ch;
  }

  function toInitials(str) {
    return Array.from(str).map(getInitial).join('');
  }

  function matchKw(post, kw) {
    var kwLower = kw.toLowerCase();
    var kwInit = toInitials(kw);
    var fields = [post.title, post.category, post.summary].map(function (s) {
      return (s || '').toLowerCase();
    });
    return fields.some(function (f) { return f.indexOf(kwLower) !== -1; }) ||
      fields.some(function (f) { return toInitials(f).indexOf(kwInit) !== -1; });
  }

  function search(query) {
    var keywords = query.trim().split(/\s+/).filter(Boolean);
    if (!keywords.length) return [];
    return posts.filter(function (post) {
      return keywords.every(function (kw) { return matchKw(post, kw); });
    });
  }

  function closeDropdown() {
    var dropdown = document.getElementById('search-results');
    if (dropdown) dropdown.classList.remove('open');
  }

  function renderDropdown(results) {
    var dropdown = document.getElementById('search-results');
    if (!dropdown) return;
    if (!results.length) {
      dropdown.innerHTML = '<div class="search-no-result">검색 결과가 없습니다.</div>';
      dropdown.classList.add('open');
      return;
    }
    dropdown.innerHTML = results.slice(0, 6).map(function (p) {
      return '<a class="search-result-item" href="' + p.url + '">' +
        '<div class="sri-title">' + p.title + '</div>' +
        '<div class="sri-meta">' + p.date + ' · ' + p.category + '</div>' +
        '</a>';
    }).join('');
    dropdown.classList.add('open');
  }

  function init() {
    var input = document.getElementById('search-input');
    if (!input) return;

    fetch('data/posts.json')
      .then(function (r) { return r.json(); })
      .then(function (data) { posts = data; })
      .catch(function () {});

    input.addEventListener('input', function () {
      var q = this.value.trim();
      if (!q) { closeDropdown(); return; }
      renderDropdown(search(q));
    });

    input.addEventListener('focus', function () {
      var q = this.value.trim();
      if (q) renderDropdown(search(q));
    });

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { closeDropdown(); this.blur(); }
    });

    document.addEventListener('click', function (e) {
      var wrapper = document.querySelector('.search-bar');
      if (wrapper && !wrapper.contains(e.target)) closeDropdown();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
