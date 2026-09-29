/* Human-friendly geography selectors for public API tools. Codes stay internal. */
(function () {
  "use strict";

  var STATES = [
    ["AL","Alabama","01"],["AK","Alaska","02"],["AZ","Arizona","04"],["AR","Arkansas","05"],["CA","California","06"],
    ["CO","Colorado","08"],["CT","Connecticut","09"],["DE","Delaware","10"],["DC","District of Columbia","11"],["FL","Florida","12"],
    ["GA","Georgia","13"],["HI","Hawaii","15"],["ID","Idaho","16"],["IL","Illinois","17"],["IN","Indiana","18"],
    ["IA","Iowa","19"],["KS","Kansas","20"],["KY","Kentucky","21"],["LA","Louisiana","22"],["ME","Maine","23"],
    ["MD","Maryland","24"],["MA","Massachusetts","25"],["MI","Michigan","26"],["MN","Minnesota","27"],["MS","Mississippi","28"],
    ["MO","Missouri","29"],["MT","Montana","30"],["NE","Nebraska","31"],["NV","Nevada","32"],["NH","New Hampshire","33"],
    ["NJ","New Jersey","34"],["NM","New Mexico","35"],["NY","New York","36"],["NC","North Carolina","37"],["ND","North Dakota","38"],
    ["OH","Ohio","39"],["OK","Oklahoma","40"],["OR","Oregon","41"],["PA","Pennsylvania","42"],["RI","Rhode Island","44"],
    ["SC","South Carolina","45"],["SD","South Dakota","46"],["TN","Tennessee","47"],["TX","Texas","48"],["UT","Utah","49"],
    ["VT","Vermont","50"],["VA","Virginia","51"],["WA","Washington","53"],["WV","West Virginia","54"],["WI","Wisconsin","55"],["WY","Wyoming","56"]
  ];

  var byFips = {};
  STATES.forEach(function (item) { byFips[item[2]] = item[0]; });

  function populateState(select, valueMode) {
    if (!select) return;
    STATES.forEach(function (item) {
      var option = document.createElement("option");
      option.value = valueMode === "fips" ? item[2] : item[0];
      option.textContent = item[1];
      select.appendChild(option);
    });
  }

  populateState(document.getElementById("facility-state"), "abbr");
  populateState(document.getElementById("trials-state"), "abbr");
  populateState(document.getElementById("cdc-state"), "abbr");
  populateState(document.getElementById("census-state"), "fips");

  var countyCache = {};
  function countiesForState(abbr) {
    if (!countyCache[abbr]) {
      countyCache[abbr] = fetch("/api/live/cdc/counties?state=" + encodeURIComponent(abbr), {
        headers: { "Accept": "application/json" }
      }).then(function (response) {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return response.json();
      }).then(function (data) {
        if (data.status !== "ok" || !(data.counties || []).length) {
          throw new Error(data.detail || "No counties returned");
        }
        return data.counties;
      }).catch(function (error) {
        delete countyCache[abbr];
        throw error;
      });
    }
    return countyCache[abbr];
  }

  function wireCountySelector(options) {
    var stateSelect = document.getElementById(options.stateId);
    var countySelect = document.getElementById(options.countyId);
    var submit = document.getElementById(options.submitId);
    var panel = document.getElementById(options.panelId);
    if (!stateSelect || !countySelect || !submit) return;

    function resetCounty(message) {
      countySelect.innerHTML = '<option value="">' + (message || "Choose county") + "</option>";
      countySelect.disabled = true;
      submit.disabled = true;
    }

    resetCounty("Choose state first");

    stateSelect.addEventListener("change", function () {
      var stateValue = stateSelect.value;
      var abbr = options.stateValue === "fips" ? byFips[stateValue] : stateValue;
      if (!abbr) {
        resetCounty("Choose state first");
        return;
      }
      resetCounty("Loading counties…");
      if (panel) panel.innerHTML = "";
      countiesForState(abbr).then(function (counties) {
        countySelect.innerHTML = '<option value="">Choose county</option>';
        counties.forEach(function (county) {
          var option = document.createElement("option");
          option.value = options.countyValue === "county_fips" ? county.fips.slice(2) : county.fips;
          option.textContent = county.name;
          countySelect.appendChild(option);
        });
        countySelect.disabled = false;
      }).catch(function () {
        resetCounty("Counties unavailable");
        if (panel) panel.innerHTML = '<div class="error"><strong>County list unavailable.</strong> Please try again.</div>';
      });
    });

    countySelect.addEventListener("change", function () {
      var valid = options.countyValue === "county_fips" ? /^\d{3}$/.test(countySelect.value) : /^\d{5}$/.test(countySelect.value);
      submit.disabled = !valid;
      if (panel) panel.innerHTML = "";
    });
  }

  wireCountySelector({
    stateId: "cdc-state",
    countyId: "cdc-county-fips",
    submitId: "cdc-county-submit",
    panelId: "cdc-county-panel",
    stateValue: "abbr",
    countyValue: "full_fips"
  });

  wireCountySelector({
    stateId: "census-state",
    countyId: "census-county",
    submitId: "census-submit",
    panelId: "census-panel",
    stateValue: "fips",
    countyValue: "county_fips"
  });
})();
