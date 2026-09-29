/* Ad-hoc PubMed search for resources.html. Renders citation cards only. */
(function () {
  "use strict";

  var form = document.getElementById("evidence-search-form");
  var panel = document.getElementById("evidence-search-results");
  if (!form || !panel) return;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function sourceNote(text) {
    return '<p class="source-note">Source: ' + esc(text) + "</p>";
  }

  function unavailableBox(reason, detail) {
    return '<div class="error"><strong>Not available right now.</strong> ' +
      esc(reason || "The source did not respond.") +
      (detail ? " " + esc(detail) : "") + "</div>";
  }

  function evidenceItem(article) {
    return '<article class="evidence-item">' +
      '<p class="ama">' + esc(article.ama11_citation || article.title || "") + " " +
      '<a href="' + esc(article.url || "#") + '" target="_blank" rel="noopener">PubMed ↗</a></p>' +
      "</article>";
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var q = document.getElementById("evidence-search-term").value.trim();
    if (!q) {
      panel.innerHTML = '<p class="muted">Enter a topic to search PubMed.</p>';
      return;
    }

    panel.innerHTML = '<p class="muted">Searching PubMed…</p>';
    fetch("/api/live/evidence-search?q=" + encodeURIComponent(q), {
      headers: { "Accept": "application/json" }
    }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    }).then(function (d) {
      if (d.status !== "ok") {
        panel.innerHTML = unavailableBox(d.reason_code || d.status, d.detail);
        return;
      }
      var articles = d.recent || [];
      var html = '<h4>PubMed results for “' + esc(d.query || q) + '”</h4>' +
        '<p class="muted">' + esc(String(d.total_results || 0)) +
        ' indexed results. Showing the most recent matches; search hits are not quality-appraised project findings.</p>';
      html += articles.length ? articles.map(evidenceItem).join("") :
        '<p class="muted">No matching articles found.</p>';
      html += sourceNote(
        (d.source || "PubMed E-utilities") +
        (d.fetched_at ? " · fetched " + d.fetched_at.slice(0, 10) : "")
      );
      panel.innerHTML = html;
    }).catch(function () {
      panel.innerHTML = unavailableBox("PubMed search did not respond.");
    });
  });
})();
