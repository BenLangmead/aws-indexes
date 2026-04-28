/**
 * Wrap each markdown table that follows .datatable-begin in .table-scroll for horizontal scroll.
 */
(function () {
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
})();
