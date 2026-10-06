/* Dartmouth Atlas explorer — Resources page. Simple human UI over APE JSON endpoints. */
(function () {
  "use strict";

  var form = document.getElementById("atlas-form");
  var datasetEl = document.getElementById("atlas-dataset");
  var areaEl = document.getElementById("atlas-area");
  var measureEl = document.getElementById("atlas-measure");
  var submitEl = document.getElementById("atlas-submit");
  var resultsEl = document.getElementById("atlas-results");
  if (!form || !datasetEl || !areaEl || !measureEl || !resultsEl) return;

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

  function setBusy(message) {
    resultsEl.innerHTML = '<p class="muted">' + esc(message) + "</p>";
  }

  function loadOptions() {
    var dataset = datasetEl.value;
    areaEl.disabled = true;
    measureEl.disabled = true;
    submitEl.disabled = true;
    areaEl.innerHTML = '<option value="">Loading areas…</option>';
    measureEl.innerHTML = '<option value="">Loading measures…</option>';
    if (!dataset) return;

    getJSON("/api/live/dartmouth-atlas/options?dataset=" + encodeURIComponent(dataset)).then(function (data) {
      if (data.status !== "ok") throw new Error(data.reason_code || data.status);
      areaEl.innerHTML = '<option value="">Choose area</option>' +
        (data.areas || []).map(function (area) { return option(area, area); }).join("");
      measureEl.innerHTML = '<option value="">Choose measure</option>' +
        (data.measures || []).map(function (measure) { return option(measure.id, measure.label); }).join("");
      areaEl.disabled = false;
      measureEl.disabled = false;
      submitEl.disabled = false;
      resultsEl.innerHTML = "";
    }).catch(function () {
      areaEl.innerHTML = '<option value="">Unavailable</option>';
      measureEl.innerHTML = '<option value="">Unavailable</option>';
      resultsEl.innerHTML = '<div class="error"><strong>Not available right now.</strong> Dartmouth Atlas did not respond.</div>';
    });
  }

  getJSON("/api/live/dartmouth-atlas/catalog").then(function (data) {
    datasetEl.innerHTML = '<option value="">Choose dataset</option>' +
      (data.datasets || []).map(function (dataset) { return option(dataset.id, dataset.label); }).join("");
  }).catch(function () {
    datasetEl.innerHTML = '<option value="">Dartmouth Atlas unavailable</option>';
  });

  datasetEl.addEventListener("change", loadOptions);

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var dataset = datasetEl.value;
    var area = areaEl.value;
    var measure = measureEl.value;
    if (!dataset || !area || !measure) {
      resultsEl.innerHTML = '<p class="muted">Choose a dataset, area, and measure.</p>';
      return;
    }
    setBusy("Loading Dartmouth Atlas…");
    getJSON(
      "/api/live/dartmouth-atlas/value?dataset=" + encodeURIComponent(dataset) +
      "&area=" + encodeURIComponent(area) +
      "&measure=" + encodeURIComponent(measure)
    ).then(function (data) {
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
    }).catch(function () {
      resultsEl.innerHTML = '<div class="error"><strong>Not available right now.</strong> Dartmouth Atlas did not respond.</div>';
    });
  });
})();
