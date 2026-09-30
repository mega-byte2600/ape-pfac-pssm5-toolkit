/* CMS HCAHPS explorer for resources.html.
   Public aggregate data only. No API key is required. */
(function () {
  "use strict";

  var form = document.getElementById("hcahps-explorer-form");
  var results = document.getElementById("hcahps-explorer-results");
  var panel = document.getElementById("hcahps-explorer-panel");
  var stateSelect = document.getElementById("hcahps-explorer-state");
  if (!form || !results || !panel || !stateSelect) return;

  var STATES = [
    ["AL","Alabama"],["AK","Alaska"],["AZ","Arizona"],["AR","Arkansas"],["CA","California"],
    ["CO","Colorado"],["CT","Connecticut"],["DE","Delaware"],["DC","District of Columbia"],["FL","Florida"],
    ["GA","Georgia"],["HI","Hawaii"],["ID","Idaho"],["IL","Illinois"],["IN","Indiana"],
    ["IA","Iowa"],["KS","Kansas"],["KY","Kentucky"],["LA","Louisiana"],["ME","Maine"],
    ["MD","Maryland"],["MA","Massachusetts"],["MI","Michigan"],["MN","Minnesota"],["MS","Mississippi"],
    ["MO","Missouri"],["MT","Montana"],["NE","Nebraska"],["NV","Nevada"],["NH","New Hampshire"],
    ["NJ","New Jersey"],["NM","New Mexico"],["NY","New York"],["NC","North Carolina"],["ND","North Dakota"],
    ["OH","Ohio"],["OK","Oklahoma"],["OR","Oregon"],["PA","Pennsylvania"],["RI","Rhode Island"],
    ["SC","South Carolina"],["SD","South Dakota"],["TN","Tennessee"],["TX","Texas"],["UT","Utah"],
    ["VT","Vermont"],["VA","Virginia"],["WA","Washington"],["WV","West Virginia"],["WI","Wisconsin"],["WY","Wyoming"]
  ];

  function esc(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (c) {
      return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];
    });
  }

  function getJSON(url) {
    return fetch(url, {headers: {"Accept": "application/json"}}).then(function (response) {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.json();
    });
  }

  function pct(value) {
    if (value == null || value === "") return "—";
    var number = Number(value);
    if (!Number.isFinite(number)) return "—";
    return (Math.round(number * 10) / 10).toString().replace(/\.0$/, "") + "%";
  }

  function bar(label, value, extraClass) {
    var number = value == null ? null : Number(value);
    var width = Number.isFinite(number) ? Math.max(0, Math.min(100, number)) : 0;
    return '<div class="bar-row"><span class="bar-key">' + esc(label) +
      '</span><div class="bar-track"><div class="bar-fill ' + esc(extraClass || "") +
      '" style="width:' + width + '%"></div></div><span class="bar-val">' + pct(value) + '</span></div>';
  }

  function periodText(period) {
    if (!period) return "not reported";
    var start = period.start || "?";
    var end = period.end || "?";
    return start + " – " + end;
  }

  STATES.forEach(function (item) {
    var option = document.createElement("option");
    option.value = item[0];
    option.textContent = item[1];
    stateSelect.appendChild(option);
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var name = document.getElementById("hcahps-explorer-name").value.trim();
    var state = stateSelect.value.trim().toUpperCase();
    if (!name && !state) {
      results.innerHTML = '<p class="muted">Enter a hospital name or choose a state.</p>';
      panel.innerHTML = "";
      return;
    }

    results.innerHTML = '<p class="muted">Searching CMS hospital records…</p>';
    panel.innerHTML = "";
    getJSON("/api/live/facility-search?name=" + encodeURIComponent(name) + "&state=" + encodeURIComponent(state))
      .then(function (data) {
        var facilities = data.facilities || [];
        if (!facilities.length) {
          results.innerHTML = '<p class="muted">No matching CMS hospitals were found. Try a shorter hospital name or another state.</p>';
          return;
        }
        results.innerHTML = '<ul class="facility-list">' + facilities.slice(0, 12).map(function (facility) {
          return '<li><button type="button" data-hcahps-facility="' + esc(facility.facility_id) + '">' +
            esc(facility.facility_name) + '<small>' + esc([facility.city, facility.state].filter(Boolean).join(", ")) +
            ' · CMS ID ' + esc(facility.facility_id) + '</small></button></li>';
        }).join("") + '</ul><p class="source-note">Source: CMS Provider Data Catalog hospital HCAHPS dataset.</p>';

        results.querySelectorAll("button[data-hcahps-facility]").forEach(function (button) {
          button.addEventListener("click", function () {
            loadComparison(button.getAttribute("data-hcahps-facility"));
          });
        });
      })
      .catch(function () {
        results.innerHTML = '<div class="error"><strong>CMS lookup is unavailable right now.</strong> No values were substituted.</div>';
      });
  });

  function loadComparison(facilityId) {
    panel.innerHTML = '<p class="muted">Loading hospital, state, and U.S. HCAHPS benchmarks…</p>';
    getJSON("/api/live/hcahps-compare?facility_id=" + encodeURIComponent(facilityId))
      .then(function (data) {
        if (data.status !== "ok") {
          panel.innerHTML = '<div class="error"><strong>HCAHPS comparison unavailable.</strong> ' +
            esc(data.detail || data.reason_code || "CMS did not return published data.") + '</div>';
          return;
        }

        var measures = (data.measures || []).filter(function (measure) {
          return measure.hospital_percent != null || measure.state_percent != null || measure.national_percent != null;
        });
        var location = [data.city, data.state].filter(Boolean).join(", ");
        var html = '<div class="hcahps-comparison-header"><h4>' + esc(data.facility_name) + '</h4>' +
          '<p class="muted">' + esc(location) + ' · CMS ID ' + esc(data.facility_id) +
          ' · public aggregate data · no API key required</p></div>';

        if (!measures.length) {
          html += '<p class="muted">CMS returned the facility but no reportable percentages for the selected measures.</p>';
        } else {
          measures.forEach(function (measure) {
            html += '<div class="measure"><div class="measure-label">' + esc(measure.label) + '</div>' +
              (measure.question ? '<div class="measure-question">' + esc(measure.question) + '</div>' : '') +
              bar("Hospital", measure.hospital_percent, "") +
              bar(data.state + " average", measure.state_percent, "state") +
              bar("U.S. average", measure.national_percent, "national") +
              '<div class="period">Hospital reporting period: ' + esc(periodText(measure.hospital_period)) + '</div>' +
              (!measure.period_alignment ? '<div class="period"><strong>Period note:</strong> state or national comparison period differs; interpret cautiously.</div>' : '') +
              '</div>';
          });
        }

        html += '<p class="muted">These are CMS HCAHPS patient-experience benchmarks. They are context signals, not evidence that PFAC activity caused a score.</p>';
        var urls = data.source_urls || {};
        html += '<p class="source-note">Sources: ' +
          (urls.hospital ? '<a href="' + esc(urls.hospital) + '" target="_blank" rel="noopener">CMS hospital HCAHPS</a>' : 'CMS hospital HCAHPS') + ' · ' +
          (urls.state ? '<a href="' + esc(urls.state) + '" target="_blank" rel="noopener">state benchmark</a>' : 'state benchmark') + ' · ' +
          (urls.national ? '<a href="' + esc(urls.national) + '" target="_blank" rel="noopener">national benchmark</a>' : 'national benchmark') +
          (data.fetched_at ? ' · fetched ' + esc(data.fetched_at.slice(0, 10)) : '') + '</p>';
        panel.innerHTML = html;
      })
      .catch(function () {
        panel.innerHTML = '<div class="error"><strong>HCAHPS comparison is unavailable right now.</strong> No values were substituted.</div>';
      });
  }
})();
