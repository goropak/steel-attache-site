/* premium-gate.js — 유료(승인제) 글 클라이언트 암호화 게이트 (재사용)
 * 동작: 본문은 AES-GCM 암호문으로 페이지에 임베드. 복호화 키는 레포에 없고,
 *       승인된 열람자에게 전달된 '키 포함 링크'(#k=...) 또는 수동 입력으로만 복호.
 * 키가 없으면 본문은 절대 복원되지 않는다(정적 사이트에서 실제 보호).
 */
(function () {
  'use strict';

  function b64ToBytes(s) {
    s = String(s || '').trim().replace(/-/g, '+').replace(/_/g, '/');
    while (s.length % 4) s += '=';
    var bin = atob(s), out = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }

  function getKeyFromHash() {
    var h = location.hash || '';
    var m = h.match(/[#&]k=([^&]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }

  function el(id) { return document.getElementById(id); }

  async function decryptAndRender(keyStr) {
    var dataEl = el('sa-premium-data');
    if (!dataEl) throw new Error('no-data');
    var pkg = JSON.parse(dataEl.textContent);
    var rawKey = b64ToBytes(keyStr);
    if (rawKey.length !== 32) throw new Error('bad-key-length');
    var key = await crypto.subtle.importKey('raw', rawKey, { name: 'AES-GCM' }, false, ['decrypt']);
    var iv = b64ToBytes(pkg.iv);
    var ct = b64ToBytes(pkg.ct);
    var plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: iv }, key, ct);
    var html = new TextDecoder().decode(plain);
    var target = el('premium-content');
    target.innerHTML = html;
    target.style.display = '';
    el('premium-gate').style.display = 'none';
    var bar = el('premium-toolbar');
    if (bar) bar.style.display = '';
    // 성공한 키를 현재 URL 해시에 보존(링크 복사가 키를 포함하도록)
    try {
      if (getKeyFromHash() !== keyStr) {
        history.replaceState(null, '', location.pathname + location.search + '#k=' + encodeURIComponent(keyStr));
      }
    } catch (e) {}
    document.title = document.title.replace(/^🔒\s*/, '');
    window.scrollTo(0, 0);
  }

  function showError(msg) {
    var e = el('premium-error');
    if (e) { e.textContent = msg; e.style.display = ''; }
  }

  async function tryUnlock(keyStr, silent) {
    if (!keyStr) { if (!silent) showError('키를 입력하세요.'); return; }
    if (!(window.crypto && crypto.subtle)) {
      showError('이 브라우저는 복호화를 지원하지 않습니다(HTTPS에서 열어주세요).');
      return;
    }
    try {
      await decryptAndRender(keyStr.trim());
    } catch (e) {
      if (!silent) showError('열람 권한이 없거나 키가 올바르지 않습니다. 관리자에게 승인 링크를 요청하세요.');
    }
  }

  function copyShareLink() {
    var key = getKeyFromHash();
    var url = location.origin + location.pathname + location.search + (key ? '#k=' + encodeURIComponent(key) : '');
    var done = function () {
      var btn = el('premium-copy');
      if (btn) { var t = btn.textContent; btn.textContent = '✓ 링크 복사됨'; setTimeout(function () { btn.textContent = t; }, 1800); }
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(done, function () { window.prompt('아래 링크를 복사하세요:', url); });
    } else {
      window.prompt('아래 링크를 복사하세요:', url);
    }
  }

  function init() {
    var unlockBtn = el('premium-unlock');
    if (unlockBtn) unlockBtn.addEventListener('click', function () { tryUnlock(el('premium-key').value, false); });
    var keyInput = el('premium-key');
    if (keyInput) keyInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') tryUnlock(keyInput.value, false); });
    var copyBtn = el('premium-copy');
    if (copyBtn) copyBtn.addEventListener('click', copyShareLink);
    var printBtn = el('premium-print');
    if (printBtn) printBtn.addEventListener('click', function () { window.print(); });
    // 링크에 키가 있으면 자동 시도
    var hk = getKeyFromHash();
    if (hk) tryUnlock(hk, true);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
