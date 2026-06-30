/* article.js — 아티클 페이지 네비게이션 (시리즈 도트·고정 바·이전/다음 카드)
   철강 주재원 · 2026-06-30 */
(function () {

  /* ── 메타 태그 읽기 ── */
  function meta(name) {
    var el = document.querySelector('meta[name="' + name + '"]');
    return el ? el.getAttribute('content') : '';
  }

  var SERIES_NAME  = meta('sa-series');
  var SERIES_NUM   = parseInt(meta('sa-series-num'), 10)  || 0;
  var SERIES_TOTAL = parseInt(meta('sa-series-total'), 10) || 0;
  var PREV_URL     = meta('sa-series-prev');
  var PREV_TITLE   = meta('sa-series-prev-title');
  var NEXT_URL     = meta('sa-series-next');
  var NEXT_TITLE   = meta('sa-series-next-title');

  /* 시리즈 아티클이 아니면 아무것도 안 함 */
  if (!SERIES_NUM || !SERIES_TOTAL) return;

  /* ── 읽기 시간 계산 ── */
  function calcReadTime() {
    var article = document.querySelector('article');
    if (!article) return 0;
    var text = article.innerText || '';
    var words = text.trim().length;
    return Math.max(1, Math.round(words / 500));
  }

  /* ── ① 상단 고정 바 삽입 ── */
  function buildProgressBar() {
    var bar = document.createElement('div');
    bar.className = 'art-topbar';
    bar.innerHTML =
      '<a class="art-back" href="../index.html">' +
        '<span class="art-back-arrow"></span>홈으로' +
      '</a>' +
      '<div class="art-progress-wrap">' +
        '<div class="art-progress-fill" id="art-progress"></div>' +
      '</div>' +
      '<div class="art-meta-right">' +
        '<span class="art-readtime">약 ' + calcReadTime() + '분</span>' +
        '<button class="art-share" id="art-share-btn" title="링크 복사">공유</button>' +
      '</div>';
    document.body.insertBefore(bar, document.body.firstChild);

    /* 스크롤 진행 표시 */
    window.addEventListener('scroll', function () {
      var docH = document.documentElement.scrollHeight - window.innerHeight;
      var pct  = docH > 0 ? Math.min(100, (window.scrollY / docH) * 100) : 0;
      var fill = document.getElementById('art-progress');
      if (fill) fill.style.width = pct + '%';

      /* 스크롤 내려가면 바 보이기 */
      bar.classList.toggle('art-topbar--visible', window.scrollY > 80);
    }, { passive: true });

    /* 공유 버튼 */
    document.getElementById('art-share-btn').addEventListener('click', function () {
      if (navigator.clipboard) {
        navigator.clipboard.writeText(location.href).then(function () {
          var btn = document.getElementById('art-share-btn');
          btn.textContent = '복사됨 ✓';
          setTimeout(function () { btn.textContent = '공유'; }, 2000);
        });
      }
    });
  }

  /* ── ② 시리즈 도트 바 삽입 ── */
  function buildSeriesDots() {
    var eyebrow = document.querySelector('.eyebrow');
    if (!eyebrow) return;

    /* 시리즈 URL 배열 — 현재 파일명 기준으로 추론 */
    var base = location.pathname.replace(/.*\//, '').replace(/\.html$/, '');
    /* base = "japan-steel-01" 형태 가정, 접두사 추출 */
    var prefix = base.replace(/-\d+$/, '-');   /* "japan-steel-" */
    var suffix = base.match(/-(\d+)$/);
    var digits = suffix ? suffix[1].length : 2; /* "01" → 2자리 */

    var strip = document.createElement('div');
    strip.className = 'series-strip';

    var label = document.createElement('div');
    label.className = 'series-strip__label';
    label.textContent = SERIES_NAME + ' — ' + SERIES_TOTAL + '부작';
    strip.appendChild(label);

    var dots = document.createElement('div');
    dots.className = 'series-strip__dots';

    for (var i = 1; i <= SERIES_TOTAL; i++) {
      /* 구분선 */
      if (i > 1) {
        var line = document.createElement('span');
        line.className = 'series-strip__line';
        dots.appendChild(line);
      }

      var num = String(i);
      while (num.length < digits) num = '0' + num;
      var url = prefix + num + '.html';

      var dot = document.createElement('a');
      dot.className = 'series-dot' +
        (i < SERIES_NUM  ? ' series-dot--done' : '') +
        (i === SERIES_NUM ? ' series-dot--cur'  : '') +
        (i > SERIES_NUM  ? ' series-dot--future' : '');
      dot.textContent = i;
      dot.title = i + '부';
      if (i !== SERIES_NUM) {
        dot.href = url;
      } else {
        dot.setAttribute('aria-current', 'true');
      }
      dots.appendChild(dot);
    }
    strip.appendChild(dots);

    /* eyebrow 바로 다음에 삽입 */
    eyebrow.parentNode.insertBefore(strip, eyebrow.nextSibling);
  }

  /* ── ③ 하단 이전/다음 카드 삽입 ── */
  function buildPostNav() {
    var notes = document.querySelector('.notes');
    if (!notes) return;

    var wrap = document.createElement('div');
    wrap.className = 'post-nav';

    if (PREV_URL) {
      var prev = document.createElement('a');
      prev.className = 'post-nav__card post-nav__card--prev';
      prev.href = PREV_URL;
      prev.innerHTML =
        '<span class="post-nav__dir">← 이전 편 · ' + (SERIES_NUM - 1) + '부</span>' +
        '<span class="post-nav__title">' + (PREV_TITLE || '이전 편') + '</span>';
      wrap.appendChild(prev);
    } else {
      wrap.appendChild(document.createElement('div')); /* 빈 자리 */
    }

    if (NEXT_URL) {
      var next = document.createElement('a');
      next.className = 'post-nav__card post-nav__card--next';
      next.href = NEXT_URL;
      next.innerHTML =
        '<span class="post-nav__dir">다음 편 · ' + (SERIES_NUM + 1) + '부 →</span>' +
        '<span class="post-nav__title">' + (NEXT_TITLE || '다음 편') + '</span>';
      wrap.appendChild(next);
    } else {
      var end = document.createElement('div');
      end.className = 'post-nav__card post-nav__card--end';
      end.innerHTML = '<span class="post-nav__dir">완결</span><span class="post-nav__title">시리즈 전체 읽기 ↑</span>';
      wrap.appendChild(end);
    }

    notes.parentNode.insertBefore(wrap, notes);
  }

  /* ── 실행 ── */
  function init() {
    buildProgressBar();
    buildSeriesDots();
    buildPostNav();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
