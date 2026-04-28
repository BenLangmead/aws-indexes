/**
 * Injects #main-content h2 headings (Markdown ##) under the current .site-nav-item.
 * Keeps fixed .site-footer below an expanded sidebar so it does not overlap the nav.
 */
(function () {
  var main = document.getElementById('main-content');
  var currentLi = document.querySelector('.site-nav-item-current');

  var used = Object.create(null);
  var ul = document.createElement('ul');
  ul.className = 'site-nav-sublist';
  ul.setAttribute('aria-label', 'Sections on this page');

  var maxItems = 50;
  var count = 0;

  if (main && currentLi) {
    var headings = main.querySelectorAll('h2');
    Array.prototype.forEach.call(headings, function (h) {
      if (count >= maxItems) return;
      var id = h.id;
      if (!id) return;
      if (used[id]) return;
      used[id] = true;

      var li = document.createElement('li');
      li.className = 'site-nav-subitem';

      var a = document.createElement('a');
      a.href = '#' + id;
      a.textContent = h.textContent.replace(/\s+/g, ' ').trim();

      li.appendChild(a);
      ul.appendChild(li);
      count++;
    });
    if (ul.children.length) currentLi.appendChild(ul);
  }

  function adjustSiteFooterClearance() {
    var footer = document.querySelector('.site-footer');
    var header = document.querySelector('.site-header');
    if (!footer || !header) return;
    if (window.matchMedia('(max-width: 960px)').matches) {
      footer.style.bottom = '';
      return;
    }
    var gap = 12;
    var defaultBottom = 40;
    var hBottom = header.getBoundingClientRect().bottom;
    var H = window.innerHeight;
    var fH = footer.getBoundingClientRect().height;
    if (hBottom + gap + fH <= H - defaultBottom) {
      footer.style.bottom = defaultBottom + 'px';
    } else {
      var b = H - hBottom - fH - gap;
      footer.style.bottom = Math.max(8, b) + 'px';
    }
  }

  var resizeScheduled = false;
  function scheduleFooterAdjust() {
    if (resizeScheduled) return;
    resizeScheduled = true;
    requestAnimationFrame(function () {
      resizeScheduled = false;
      adjustSiteFooterClearance();
    });
  }

  scheduleFooterAdjust();
  window.addEventListener('resize', scheduleFooterAdjust);
})();
