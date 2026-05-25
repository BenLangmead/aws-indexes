/**
 * When the sidebar nav column scrolls vertically, add the same edge-fade hint
 * as wide tables (.table-scroll): classes on the outer .site-nav, scroll on .site-nav-scroll.
 */
(function () {
  function debounce(fn, ms) {
    var t;
    return function () {
      clearTimeout(t);
      var args = arguments;
      t = setTimeout(function () {
        fn.apply(null, args);
      }, ms);
    };
  }

  var EPS = 3;

  function updateNavScrollHints(outer, scrollEl) {
    if (!outer || !scrollEl) return;
    var sh = scrollEl.scrollHeight;
    var ch = scrollEl.clientHeight;
    if (sh <= ch + EPS) {
      outer.classList.remove('site-nav--more-above', 'site-nav--more-below');
      return;
    }

    var st = scrollEl.scrollTop;
    var moreAbove = st > EPS;
    var moreBelow = st + ch < sh - EPS;
    outer.classList.toggle('site-nav--more-above', moreAbove);
    outer.classList.toggle('site-nav--more-below', moreBelow);
  }

  function bindNavScrollHints(outer, scrollEl) {
    function update() {
      updateNavScrollHints(outer, scrollEl);
    }
    update();
    scrollEl.addEventListener('scroll', update);
    if (typeof ResizeObserver !== 'undefined') {
      var ro = new ResizeObserver(update);
      ro.observe(scrollEl);
    }
  }

  function init() {
    var outer = document.querySelector('.site-nav');
    var scrollEl = outer && outer.querySelector('.site-nav-scroll');
    if (!outer || !scrollEl) return;
    bindNavScrollHints(outer, scrollEl);
  }

  function scheduleInit() {
    requestAnimationFrame(function () {
      requestAnimationFrame(init);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scheduleInit);
  } else {
    scheduleInit();
  }

  window.addEventListener(
    'resize',
    debounce(function () {
      var outer = document.querySelector('.site-nav');
      var scrollEl = outer && outer.querySelector('.site-nav-scroll');
      updateNavScrollHints(outer, scrollEl);
    }, 150)
  );
})();
