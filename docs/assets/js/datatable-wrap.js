/**
 * Wrap each markdown table that follows .datatable-begin in .table-scroll for horizontal scroll.
 * When the table is wider than the container, add edge gradients and a11y hints.
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

  function updateScrollHints(el) {
    var sw = el.scrollWidth;
    var cw = el.clientWidth;
    if (sw <= cw + EPS) {
      el.classList.remove(
        'table-scroll--overflow',
        'table-scroll--more-left',
        'table-scroll--more-right'
      );
      el.removeAttribute('title');
      return;
    }

    el.classList.add('table-scroll--overflow');
    var sl = el.scrollLeft;
    var moreLeft = sl > EPS;
    var moreRight = sl + cw < sw - EPS;
    el.classList.toggle('table-scroll--more-left', moreLeft);
    el.classList.toggle('table-scroll--more-right', moreRight);

    if (moreRight && moreLeft) {
      el.setAttribute('title', 'More columns on both sides — scroll horizontally');
    } else if (moreRight) {
      el.setAttribute('title', 'More columns to the right — scroll or swipe sideways');
    } else if (moreLeft) {
      el.setAttribute('title', 'More columns to the left — scroll back');
    } else {
      el.removeAttribute('title');
    }
  }

  function bindScrollHints(el) {
    updateScrollHints(el);
    el.addEventListener('scroll', function () {
      updateScrollHints(el);
    });
    if (typeof ResizeObserver !== 'undefined') {
      var ro = new ResizeObserver(function () {
        updateScrollHints(el);
      });
      ro.observe(el);
    }
  }

  function initHints() {
    document.querySelectorAll('.table-scroll').forEach(bindScrollHints);
  }

  document.querySelectorAll('.datatable-begin').forEach(function (begin) {
    var table = begin.nextElementSibling;
    if (!table || table.tagName !== 'TABLE') {
      return;
    }
    var end = table.nextElementSibling;
    var wrap = document.createElement('div');
    wrap.className = 'table-scroll';
    begin.parentNode.insertBefore(wrap, table);
    wrap.appendChild(table);
    begin.remove();
    if (end && end.classList && end.classList.contains('datatable-end')) {
      end.remove();
    }
  });

  function scheduleHints() {
    requestAnimationFrame(function () {
      requestAnimationFrame(initHints);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scheduleHints);
  } else {
    scheduleHints();
  }

  window.addEventListener(
    'resize',
    debounce(function () {
      document.querySelectorAll('.table-scroll').forEach(updateScrollHints);
    }, 150)
  );
})();
