(function () {
  var sidebar = document.getElementById('sidebar');
  var menuBtn = document.getElementById('menu-btn');
  menuBtn.addEventListener('click', function () {
    sidebar.classList.toggle('open');
  });
  sidebar.addEventListener('click', function (e) {
    if (e.target.tagName === 'A' && window.innerWidth <= 900) {
      sidebar.classList.remove('open');
    }
  });

  // Lightbox for figures
  var lightbox = document.getElementById('lightbox');
  var lightboxImg = lightbox.querySelector('img');
  document.querySelectorAll('figure img').forEach(function (img) {
    img.addEventListener('click', function () {
      lightboxImg.src = img.src;
      lightboxImg.alt = img.alt;
      lightbox.hidden = false;
    });
  });
  lightbox.addEventListener('click', function () { lightbox.hidden = true; });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') lightbox.hidden = true;
  });

  // Simple full-text search across sections/subsections
  var searchInput = document.getElementById('search');
  var resultsBox = document.getElementById('search-results');
  var units = [];
  document.querySelectorAll('.subsec[id], section[id]').forEach(function (el) {
    var heading = el.querySelector('h2, h3');
    units.push({
      id: el.id,
      title: heading ? heading.textContent : el.id,
      text: el.textContent.toLowerCase()
    });
  });

  function escapeHtml(s) {
    return s.replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  searchInput.addEventListener('input', function () {
    var q = searchInput.value.trim().toLowerCase();
    if (q.length < 2) {
      resultsBox.hidden = true;
      resultsBox.innerHTML = '';
      return;
    }
    var hits = units.filter(function (u) { return u.text.indexOf(q) !== -1; }).slice(0, 30);
    var html = '<h2>Search results for &ldquo;' + escapeHtml(searchInput.value.trim()) + '&rdquo; (' + hits.length + ')</h2>';
    hits.forEach(function (u) {
      var i = u.text.indexOf(q);
      var start = Math.max(0, i - 60);
      var snippet = escapeHtml(u.text.substr(start, 160));
      html += '<div class="hit"><a href="#' + u.id + '">' + escapeHtml(u.title) + '</a>' +
        '<div class="snippet">&hellip;' + snippet.replace(new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'), function (m) { return '<mark>' + m + '</mark>'; }) + '&hellip;</div></div>';
    });
    if (!hits.length) html += '<p>No matches found.</p>';
    resultsBox.innerHTML = html;
    resultsBox.hidden = false;
  });

  // Highlight active nav link on scroll
  var navLinks = {};
  document.querySelectorAll('.nav-subs a').forEach(function (a) {
    navLinks[a.getAttribute('href').slice(1)] = a;
  });
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      var link = navLinks[entry.target.id];
      if (link) link.classList.toggle('active', entry.isIntersecting);
    });
  }, { rootMargin: '-20% 0px -70% 0px' });
  document.querySelectorAll('.subsec[id]').forEach(function (el) { observer.observe(el); });
})();
