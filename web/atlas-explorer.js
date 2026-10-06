/* Dartmouth Atlas explorer — simple Resources-page UI over read-only APE JSON. */
(function () {
  "use strict";

  var form = document.getElementById("atlas-form");
  var datasetEl = document.getElementById("atlas-dataset");
  var areaEl = document.getElementById("atlas-area");
  var areaListEl = document.getElementById("atlas-area-list");
  var measureEl = document.getElementById("atlas-measure");
  var submitEl = document.getElementById("atlas-submit");
  var resultsEl = document.getElementById("atlas-results");
  if (!form || !datasetEl || !areaEl || !areaListEl || !measureEl || !resultsEl) return;

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

  function option(value, label) {
    return '<option value="' + esc(value) + '">' + esc(label) + "</option>";
  }

  function setUnavailable() {
    areaEl.disabled = true;
    measureEl.disabled = true;
    submitEl.disabled = true;
    resultsEl.innerHTML = '<div class="error"><strong>Not available right now.</strong> Dartmouth Atlas did not respond.</div>';
  }

  function loadOptions() {
    var dataset = datasetEl.value;
    areaEl.value = "";
    areaEl.disabled = true;
    areaListEl.innerHTML = "";
    measureEl.disabled = true;
    measureEl.innerHTML = '<option value="">Loading measures…</option>';
    submitEl.disabled = true;
    resultsEl.innerHTML = "";
    if (!dataset) return;

    getJSON("/api/live/dartmouth-atlas/options?dataset=" + encodeURIComponent(dataset)).then(function (data) {
      if (data.status !== "ok") throw new Error(data.reason_code || data.status);
      areaListEl.innerHTML = (data.areas || []).map(function (area) {
        return '<option value="' + esc(area) + '"></option>';
      }).join("");
      measureEl.innerHTML = '<option value="">Choose measure</option>' +
        (data.measures || []).map(function (measure) { return option(measure.id, measure.label); }).join("");
      areaEl.disabled = false;
      measureEl.disabled = false;
      submitEl.disabled = false;
    }).catch(setUnavailable);
  }

  getJSON("/api/live/dartmouth-atlas/catalog").then(function (data) {
    var datasets = data.datasets || [];
    datasetEl.innerHTML = datasets.map(function (dataset) {
      return option(dataset.id, dataset.label);
    }).join("");
    if (datasets.length) {
      datasetEl.value = datasets.some(function (d) { return d.id === "primary-care"; }) ? "primary-care" : datasets[0].id;
      loadOptions();
    }
  }).catch(setUnavailable);

  datasetEl.addEventListener("change", loadOptions);

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var dataset = datasetEl.value;
    var area = areaEl.value.trim();
    var measure = measureEl.value;
    if (!dataset || !area || !measure) {
      resultsEl.innerHTML = '<p class="muted">Choose a region and measure.</p>';
      return;
    }

    resultsEl.innerHTML = '<p class="muted">Loading…</p>';
    getJSON(
      "/api/live/dartmouth-atlas/value?dataset=" + encodeURIComponent(dataset) +
      "&area=" + encodeURIComponent(area) +
      "&measure=" + encodeURIComponent(measure)
    ).then(function (data) {
      if (data.status === "not_found") {
        resultsEl.innerHTML = '<p class="muted">Choose a region from the suggestions.</p>';
        return;
      }
      if (data.status !== "ok") throw new Error(data.reason_code || data.status);

      var value = data.suppressed ? "Not reportable" : (data.value == null ? "—" : data.value);
      var note = data.note ? '<p class="muted">' + esc(data.note) + "</p>" : "";
      var year = data.year ? " · " + esc(data.year) : "";
      resultsEl.innerHTML =
        '<div class="stat"><strong>' + esc(value) + '</strong><span>' +
        esc(data.measure_label) + " · " + esc(data.area) + year + "</span></div>" +
        note +
        '<p class="source-note">Source: <a href="' + esc(data.source_url) +
        '" target="_blank" rel="noopener">Dartmouth Atlas Data ↗</a> · ' +
        '<a href="' + esc(data.terms_url) + '" target="_blank" rel="noopener">terms of use ↗</a></p>';
    }).catch(setUnavailable);
  });
})();
