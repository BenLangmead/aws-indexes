/**
 * Injects #main-content h2 headings (Markdown ##) under the current .site-nav-item.
 */
(function () {
  var main = document.getElementById('main-content');
  if (!main) return;

  var currentLi = document.querySelector('.site-nav-item-current');
  if (!currentLi) return;

  var headings = main.querySelectorAll('h2');
  if (!headings.length) return;

  var used = Object.create(null);
  var ul = document.createElement('ul');
  ul.className = 'site-nav-sublist';
  ul.setAttribute('aria-label', 'Sections on this page');

  var maxItems = 50;
  var count = 0;

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

  if (!ul.children.length) return;
  currentLi.appendChild(ul);
})();
