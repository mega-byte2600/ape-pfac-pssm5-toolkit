/* Live public data — resources.html. Plain-language, executive-friendly.
   All data is public aggregate; failures render as plain messages, never fake data. */
(function () {
  "use strict";

  var statusEl = document.getElementById("live-data-status");
  var facilityForm = document.getElementById("facility-search-form");
  var facilityResults = document.getElementById("facility-results");
  var hcahpsPanel = document.getElementById("hcahps-panel");
  var trialsPanel = document.getElementById("trials-panel");
  var evidenceEl = document.getElementById("evidence-watch");
  var censusForm = document.getElementById("census-form");
  var censusPanel = document.getElementById("census-panel");

  if (!statusEl) return; // not on resources.html

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function getJSON(url) {
    return fetch(url, { headers: { "Accept": "application/json" } }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
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

  /* ---- source status pills ---- */
  getJSON("/api/live/status").then(function (st) {
    var srcs = st.sources || [];
    var pills = srcs.map(function (s) {
      var state = s.state || (s.credential_required ? "needs_key" : "live");
      var cls = "unavailable", note = s.reason || state;
      if (state === "live") { cls = "ok"; note = "live, no key"; }
      else if (state === "degraded") { cls = "degraded"; note = "slow — " + (s.reason || "responding slowly"); }
      else if (state === "needs_key") { cls = "unavailable"; note = "needs a free key"; }
      return '<span class="status-pill ' + cls + '">' + esc(s.label) + " — " + esc(note) + "</span>";
    }).join("");
    statusEl.innerHTML = pills ||
      '<span class="muted">Source status unavailable.</span>';
  }).catch(function () {
    statusEl.innerHTML = '<span class="muted">Could not reach live sources.</span>';
  });

  /* ---- facility search + HCAHPS ---- */
  facilityForm.addEventListener("submit", function (e) {
    e.preventDefault();
    var name = document.getElementById("facility-name").value.trim();
    var state = document.getElementById("facility-state").value.trim().toUpperCase();
    if (!name && !state) {
      facilityResults.innerHTML = '<p class="muted">Enter a hospital name or a two-letter state.</p>';
      return;
    }
    facilityResults.innerHTML = '<p class="muted">Searching CMS records…</p>';
    hcahpsPanel.innerHTML = "";
    getJSON("/api/live/facility-search?name=" + encodeURIComponent(name) +
            "&state=" + encodeURIComponent(state)).then(function (d) {
      var list = d.facilities || [];
      if (!list.length) {
        facilityResults.innerHTML = '<p class="muted">No hospitals found. Try a shorter name or a different state.</p>' +
          sourceNote(d.source || "CMS Provider Data Catalog");
        return;
      }
      var html = '<ul class="facility-list">' + list.slice(0, 12).map(function (f) {
        return '<li><button type="button" data-facility-id="' + esc(f.facility_id) + '"' +
          ' data-facility-name="' + esc(f.facility_name) + '"' +
          ' data-facility-state="' + esc(f.state) + '">' +
          esc(f.facility_name) +
          "<small>" + esc([f.city, f.state].filter(Boolean).join(", ")) +
          " · CMS ID " + esc(f.facility_id) + "</small></button></li>";
      }).join("") + "</ul>";
      if (list.length > 12) html += '<p class="muted">Showing 12 of ' + list.length + ". Narrow your search.</p>";
      facilityResults.innerHTML = html + sourceNote(d.source || "CMS Provider Data Catalog");
      facilityResults.querySelectorAll("button[data-facility-id]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          loadHcahps(btn.getAttribute("data-facility-id"));
          loadTrials(btn.getAttribute("data-facility-name"), btn.getAttribute("data-facility-state"));
        });
      });
    }).catch(function () {
      facilityResults.innerHTML = unavailableBox("CMS facility search did not respond.");
    });
  });

  function loadHcahps(facilityId) {
    hcahpsPanel.innerHTML = '<p class="muted">Loading experience scores…</p>';
    getJSON("/api/live/hcahps?facility_id=" + encodeURIComponent(facilityId)).then(function (d) {
      if (d.status !== "ok") {
        hcahpsPanel.innerHTML = unavailableBox(d.reason_code || d.status, d.detail);
        return;
      }
      var measures = (d.measures || []).filter(function (m) {
        return m.facility_percent != null && m.national_percent != null;
      });
      var html = "<h4>" + esc(d.facility_name || ("Facility " + d.facility_id)) + "</h4>";
      if (!measures.length) {
        html += '<p class="muted">CMS has no published HCAHPS scores for this facility in the current period.</p>';
      } else {
        html += measures.map(function (m) {
          var f = Number(m.facility_percent), n = Number(m.national_percent);
          return '<div class="measure">' +
            '<div class="measure-label">' + esc(m.label) + "</div>" +
            (m.question ? '<div class="measure-question">' + esc(m.question) + "</div>" : "") +
            barRow("This hospital", f, false) +
            barRow("National average", n, true) +
            '<div class="period">Reporting period: ' + esc(m.period_start || "?") + " – " + esc(m.period_end || "?") + "</div>" +
            "</div>";
        }).join("");
        html += '<p class="muted">These scores describe patient experience. They do not show what caused a score to move.</p>';
      }
      hcahpsPanel.innerHTML = html + sourceNote(
        (d.source || "CMS Provider Data Catalog") +
        (d.fetched_at ? " · fetched " + d.fetched_at.slice(0, 10) : ""));
    }).catch(function () {
      hcahpsPanel.innerHTML = unavailableBox("HCAHPS data did not respond.");
    });
  }

  function loadTrials(facilityName, state) {
    if (!trialsPanel) return;
    trialsPanel.innerHTML = '<p class="muted">Loading research at this hospital…</p>';
    getJSON("/api/live/trials?facility_name=" + encodeURIComponent(facilityName || "") +
            "&state=" + encodeURIComponent(state || "")).then(function (d) {
      if (d.status !== "ok") {
        trialsPanel.innerHTML = unavailableBox(d.reason_code || d.status, d.detail);
        return;
      }
      var studies = d.studies || [];
      var html = "<h4>Research engagement at " + esc(facilityName || "this hospital") + "</h4>";
      html += '<p class="muted">Studies listing this hospital as a location. Recruiting studies are where advisor input on recruitment and participant experience counts most. Listings are informational — whether advisors engage with any study is your call.</p>';
      if (!studies.length) {
        html += '<p class="muted">No matching trials found for this hospital right now.</p>';
      } else {
        html += '<ul class="trial-list">' + studies.map(function (s) {
          var locs = (s.locations || []).map(function (l) {
            return [l.facility, l.city, l.state].filter(Boolean).join(", ");
          }).join(" · ");
          var recruiting = (s.status || "").toUpperCase() === "RECRUITING";
          return '<li class="trial-item' + (recruiting ? " recruiting" : "") + '">' +
            '<div class="trial-title"><a href="' + esc(s.url) + '" target="_blank" rel="noopener">' +
            esc(s.title || s.nct_id) + ' ↗</a></div>' +
            '<div class="trial-meta"><span class="trial-status">' + esc(s.status || "—") + "</span>" +
            (s.phase ? ' <span class="trial-phase">' + esc(s.phase) + "</span>" : "") +
            ' <span class="trial-nct">' + esc(s.nct_id) + "</span></div>" +
            (locs ? '<div class="trial-locs">' + esc(locs) + "</div>" : "") +
            "</li>";
        }).join("") + "</ul>";
      }
      trialsPanel.innerHTML = html + sourceNote(
        (d.source || "ClinicalTrials.gov") +
        (d.fetched_at ? " · fetched " + d.fetched_at.slice(0, 10) : ""));
    }).catch(function () {
      trialsPanel.innerHTML = unavailableBox("ClinicalTrials.gov did not respond.");
    });
  }

  function barRow(key, val, national) {
    var pct = Math.max(0, Math.min(100, val));
    return '<div class="bar-row"><span class="bar-key">' + esc(key) + "</span>" +
      '<div class="bar-track"><div class="bar-fill' + (national ? " national" : "") +
      '" style="width:' + pct + '%"></div></div>' +
      '<span class="bar-val">' + pct + "%</span></div>";
  }

  /* ---- evidence watch ---- */
  getJSON("/api/live/evidence-watch").then(function (d) {
    if (d.status !== "ok") {
      evidenceEl.innerHTML = unavailableBox(d.reason_code || d.status, d.detail);
      return;
    }
    var watches = d.watches || [];
    var labels = {
      "pfac_systematic_reviews": "PFAC systematic reviews",
      "engagement_outcomes": "Patient engagement & outcomes"
    };
    var html = "";
    watches.forEach(function (w) {
      var tag = labels[w.watch_id] || w.watch_id;
      (w.recent || []).forEach(function (a) {
        html += '<article class="evidence-item"><span class="watch-tag">' +
          esc(tag) + " · " + esc(String(w.total_results)) + " found</span>" +
          '<p class="ama">' + esc(a.ama11_citation || a.title || "") + " " +
          '<a href="' + esc(a.url) + '" target="_blank" rel="noopener">PubMed ↗</a></p></article>';
      });
    });
    evidenceEl.innerHTML = html ||
      '<p class="muted">No new articles matched this week.</p>';
    evidenceEl.innerHTML += sourceNote(
      (d.source || "PubMed E-utilities") +
      (d.fetched_at ? " · fetched " + d.fetched_at.slice(0, 10) : "") +
      " · citations in AMA 11th edition format");
  }).catch(function () {
    evidenceEl.innerHTML = unavailableBox("PubMed surveillance did not respond.");
  });

  /* ---- census demographics ---- */
  censusForm.addEventListener("submit", function (e) {
    e.preventDefault();
    var sf = document.getElementById("census-state").value.trim();
    var cf = document.getElementById("census-county").value.trim();
    if (!sf || !cf) {
      censusPanel.innerHTML = '<p class="muted">Enter both a state and county FIPS code.</p>';
      return;
    }
    censusPanel.innerHTML = '<p class="muted">Looking up…</p>';
    getJSON("/api/live/census-demographics?state_fips=" + encodeURIComponent(sf) +
            "&county_fips=" + encodeURIComponent(cf)).then(function (d) {
      if (d.status !== "ok") {
        var msg = (d.reason_code === "CREDENTIALS_NOT_CONFIGURED")
          ? "Population lookup needs a free Census API key on the server. Until then, the static county tables in the toolkit still work."
          : (d.reason_code || d.status);
        censusPanel.innerHTML = unavailableBox(msg, d.detail);
        return;
      }
      var subs = d.subdivisions || [];
      var total = subs.reduce(function (acc, s) {
        var n = Number(String(s.population).replace(/[^0-9]/g, ""));
        return acc + (isNaN(n) ? 0 : n);
      }, 0);
      var html = "<h4>County subdivisions</h4>";
      if (!subs.length) {
        html += '<p class="muted">No subdivision data returned for this county.</p>';
      } else {
        html += '<div class="stat-grid">' +
          '<div class="stat"><strong>' + total.toLocaleString() + '</strong><span>Total population</span></div>' +
          '<div class="stat"><strong>' + subs.length + '</strong><span>Subdivisions</span></div>' +
          "</div>";
        html += '<ul class="facility-list">' + subs.slice(0, 20).map(function (s) {
          return "<li><button type=\"button\" disabled>" + esc(s.name || "—") +
            "<small>Population " + esc(String(s.population == null ? "—" : s.population)) +
            (s.poverty_percent != null ? " · " + esc(String(s.poverty_percent)) + "% below poverty" : "") +
            "</small></button></li>";
        }).join("") + "</ul>";
        if (subs.length > 20) html += '<p class="muted">Showing 20 of ' + subs.length + " subdivisions.</p>";
      }
      censusPanel.innerHTML = html + sourceNote(
        (d.source || "U.S. Census Bureau, American Community Survey 5-year") +
        (d.fetched_at ? " · fetched " + d.fetched_at.slice(0, 10) : ""));
    }).catch(function () {
      censusPanel.innerHTML = unavailableBox("Census lookup did not respond.");
    });
  });
})();
