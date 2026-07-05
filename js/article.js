/* article.js — 아티클 네비게이션 v2
   철강 주재원 · 2026-06-30
   인라인 스타일 방식 — CSS 로딩 여부와 무관하게 동작 */
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

  if (!SERIES_NUM || !SERIES_TOTAL) return;

  /* ── 스타일 시트 주입 (한 번만) ── */
  function injectStyles() {
    if (document.getElementById('art-nav-style')) return;
    var s = document.createElement('style');
    s.id = 'art-nav-style';
    s.textContent = [
      /* 상단 고정 바 */
      '.art-topbar{position:fixed;top:0;left:0;right:0;z-index:9999;',
        'display:none;align-items:center;gap:12px;padding:0 20px;height:44px;',
        'background:rgba(17,22,29,.97);border-bottom:1px solid rgba(255,255,255,.07);}',
      '.art-topbar.on{display:flex;}',
      '.art-back{display:flex;align-items:center;gap:8px;font-size:.8rem;',
        'color:#c8c2ba;text-decoration:none;white-space:nowrap;flex-shrink:0;}',
      '.art-back:hover{color:#fff;}',
      '.art-back-arr{display:inline-block;width:8px;height:8px;',
        'border-left:2px solid #D62828;border-bottom:2px solid #D62828;',
        'transform:rotate(45deg);}',
      '.art-prog-wrap{flex:1;height:3px;background:rgba(255,255,255,.15);border-radius:2px;overflow:hidden;}',
      '.art-prog-fill{height:100%;width:0;background:#D62828;border-radius:2px;transition:width .1s linear;}',
      '.art-share{background:none;border:1px solid rgba(255,255,255,.25);border-radius:4px;',
        'color:#c8c2ba;font-size:.75rem;padding:3px 10px;cursor:pointer;}',
      '.art-share:hover{border-color:#D62828;color:#fff;}',
      /* 시리즈 도트 바 */
      '.series-strip{margin:.8rem 0 1.6rem;padding:14px 18px;',
        'background:#f5f3ee;border:1px solid #e6e0d4;border-radius:10px;}',
      '.series-strip__lbl{font-size:.72rem;color:#9a8a7a;margin-bottom:10px;letter-spacing:.04em;}',
      '.series-strip__dots{display:flex;align-items:center;}',
      '.series-strip__line{flex:1;height:2px;background:#e0dbd2;}',
      '.sdot{width:32px;height:32px;border-radius:50%;display:flex;align-items:center;',
        'justify-content:center;font-size:.78rem;font-weight:700;text-decoration:none;flex-shrink:0;}',
      '.sdot-done{background:#ddd8cf;color:#9a8a7a;}',
      '.sdot-cur{background:#D62828;color:#fff;box-shadow:0 2px 8px rgba(214,40,40,.35);}',
      '.sdot-future{background:#fff;border:2px solid #e0dbd2;color:#bbb;}',
      '.sdot-done:hover,.sdot-future:hover{transform:scale(1.1);}',
      /* 이전/다음 카드 */
      '.post-nav{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:2.4rem 0 2rem;}',
      '.pnav-card{display:flex;flex-direction:column;gap:6px;padding:16px 18px;',
        'border-radius:10px;background:#11161d;text-decoration:none;}',
      '.pnav-card:hover{background:#1c2330;}',
      '.pnav-next{align-items:flex-end;text-align:right;}',
      '.pnav-dir{font-size:.72rem;color:#D62828;font-weight:600;}',
      '.pnav-title{font-size:.88rem;color:#e8e3da;font-weight:600;line-height:1.45;}',
      '@media(max-width:560px){.post-nav{grid-template-columns:1fr;}',
        '.pnav-next{align-items:flex-start;text-align:left;}}'
    ].join('');
    document.head.appendChild(s);
  }

  /* ── ① 상단 고정 바 ── */
  function buildTopBar() {
    var bar = document.createElement('div');
    bar.className = 'art-topbar';
    bar.innerHTML =
      '<a class="art-back" href="../index.html">' +
        '<span class="art-back-arr"></span>홈으로' +
      '</a>' +
      '<div class="art-prog-wrap"><div class="art-prog-fill" id="art-pf"></div></div>' +
      '<button class="art-share" id="art-share">공유</button>';
    document.body.insertBefore(bar, document.body.firstChild);

    window.addEventListener('scroll', function () {
      var docH = document.documentElement.scrollHeight - window.innerHeight;
      var pct  = docH > 0 ? Math.min(100, (window.scrollY / docH) * 100) : 0;
      var fill = document.getElementById('art-pf');
      if (fill) fill.style.width = pct + '%';
      bar.classList.toggle('on', window.scrollY > 80);
    }, { passive: true });

    document.getElementById('art-share').addEventListener('click', function () {
      var btn = document.getElementById('art-share');
      if (navigator.clipboard) {
        navigator.clipboard.writeText(location.href).then(function () {
          btn.textContent = '복사됨 ✓';
          setTimeout(function () { btn.textContent = '공유'; }, 2000);
        });
      } else {
        /* 구형 브라우저 fallback */
        prompt('URL을 복사하세요:', location.href);
      }
    });
  }

  /* ── ② 시리즈 도트 바 ── */
  function buildSeriesDots() {
    var eyebrow = document.querySelector('.eyebrow');
    if (!eyebrow) return;

    var base   = location.pathname.replace(/.*\//, '').replace(/\.html$/, '');
    var prefix = base.replace(/-\d+$/, '-');
    var dlen   = (base.match(/-(\d+)$/) || [,'01'])[1].length;

    var strip = document.createElement('div');
    strip.className = 'series-strip';

    var lbl = document.createElement('div');
    lbl.className = 'series-strip__lbl';
    lbl.textContent = SERIES_NAME + ' — ' + SERIES_TOTAL + '부작';
    strip.appendChild(lbl);

    var dots = document.createElement('div');
    dots.className = 'series-strip__dots';

    for (var i = 1; i <= SERIES_TOTAL; i++) {
      if (i > 1) {
        var ln = document.createElement('span');
        ln.className = 'series-strip__line';
        dots.appendChild(ln);
      }
      var n = String(i);
      while (n.length < dlen) n = '0' + n;

      var dot = document.createElement('a');
      dot.textContent = i;
      dot.title = i + '부';

      if (i === SERIES_NUM) {
        dot.className = 'sdot sdot-cur';
        dot.setAttribute('aria-current', 'true');
      } else if (i < SERIES_NUM) {
        dot.className = 'sdot sdot-done';
        dot.href = prefix + n + '.html';
      } else {
        dot.className = 'sdot sdot-future';
        dot.href = prefix + n + '.html';
      }
      dots.appendChild(dot);
    }
    strip.appendChild(dots);
    eyebrow.parentNode.insertBefore(strip, eyebrow.nextSibling);
  }

  /* ── ③ 이전/다음 카드 ── */
  function buildPostNav() {
    var notes = document.querySelector('.notes');
    if (!notes) return;

    var wrap = document.createElement('div');
    wrap.className = 'post-nav';

    /* 이전 편 */
    if (PREV_URL) {
      var prev = document.createElement('a');
      prev.className = 'pnav-card';
      prev.href = PREV_URL;
      prev.innerHTML =
        '<span class="pnav-dir">← ' + (SERIES_NUM - 1) + '부</span>' +
        '<span class="pnav-title">' + (PREV_TITLE || '이전 편') + '</span>';
      wrap.appendChild(prev);
    } else {
      wrap.appendChild(document.createElement('div'));
    }

    /* 다음 편 */
    if (NEXT_URL) {
      var next = document.createElement('a');
      next.className = 'pnav-card pnav-next';
      next.href = NEXT_URL;
      next.innerHTML =
        '<span class="pnav-dir">' + (SERIES_NUM + 1) + '부 →</span>' +
        '<span class="pnav-title">' + (NEXT_TITLE || '다음 편') + '</span>';
      wrap.appendChild(next);
    } else {
      var end = document.createElement('div');
      end.className = 'pnav-card';
      end.style.alignItems = 'center';
      end.style.textAlign = 'center';
      end.style.opacity = '.5';
      end.innerHTML =
        '<span class="pnav-dir">완결</span>' +
        '<span class="pnav-title">시리즈 전체 읽기 ↑</span>';
      wrap.appendChild(end);
    }

    notes.parentNode.insertBefore(wrap, notes);
  }

  function init() {
    injectStyles();
    buildTopBar();
    buildSeriesDots();
    buildPostNav();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
