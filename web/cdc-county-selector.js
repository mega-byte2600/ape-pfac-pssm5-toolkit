/* CDC county selector: users choose a state and county; FIPS stays internal. */
(function () {
  "use strict";

  var stateSelect = document.getElementById("cdc-state");
  var countySelect = document.getElementById("cdc-county-fips");
  var panel = document.getElementById("cdc-county-panel");
  var submit = document.getElementById("cdc-county-submit");
  if (!stateSelect || !countySelect || !submit) return;

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

  STATES.forEach(function (item) {
    var option = document.createElement("option");
    option.value = item[0];
    option.textContent = item[1];
    stateSelect.appendChild(option);
  });

  function resetCounty(message) {
    countySelect.innerHTML = '<option value="">' + (message || "Choose county") + "</option>";
    countySelect.disabled = true;
    submit.disabled = true;
  }

  resetCounty("Choose state first");

  stateSelect.addEventListener("change", function () {
    var state = stateSelect.value;
    if (!state) {
      resetCounty("Choose state first");
      return;
    }
    resetCounty("Loading counties…");
    if (panel) panel.innerHTML = "";
    fetch("/api/live/cdc/counties?state=" + encodeURIComponent(state), {
      headers: { "Accept": "application/json" }
    }).then(function (response) {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.json();
    }).then(function (data) {
      if (data.status !== "ok" || !(data.counties || []).length) {
        throw new Error(data.detail || "No counties returned");
      }
      countySelect.innerHTML = '<option value="">Choose county</option>';
      data.counties.forEach(function (county) {
        var option = document.createElement("option");
        option.value = county.fips;
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
    submit.disabled = !/^\d{5}$/.test(countySelect.value);
    if (panel) panel.innerHTML = "";
  });
})();
