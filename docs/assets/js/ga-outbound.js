/**
 * GA4: record outbound link clicks (other hostnames, e.g. S3, GitHub, docs).
 * Requires gtag from the Google tag snippet (loaded in the layout when GA4 is enabled).
 */
(function () {
  if (typeof gtag !== 'function') return;

  document.addEventListener(
    'click',
    function (e) {
      var a = e.target && e.target.closest && e.target.closest('a[href]');
      if (!a) return;
      var href = a.getAttribute('href');
      if (!href || href.charAt(0) === '#' || href.indexOf('mailto:') === 0) return;
      try {
        var u = new URL(a.href, window.location.href);
        if (u.protocol !== 'http:' && u.protocol !== 'https:') return;
        if (u.hostname === window.location.hostname) return;
        gtag('event', 'outbound_click', {
          link_url: u.href,
          link_domain: u.hostname,
          link_text: (a.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 120),
          transport_type: 'beacon',
        });
      } catch (err) {
        /* ignore invalid URLs */
      }
    },
    true
  );
})();
