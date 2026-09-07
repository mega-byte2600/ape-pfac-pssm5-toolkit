async function fetchJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) throw new Error(`${path} returned ${response.status}`);
  return response.json();
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text) node.textContent = text;
  return node;
}

function fillQuestions(items) {
  const target = document.getElementById("questions");
  target.innerHTML = "";
  for (const item of items) target.appendChild(el("div", "question", item));
}

function fillMetrics(items) {
  const target = document.getElementById("metric-grid");
  target.innerHTML = "";
  for (const item of items) {
    const article = el("article", "card metric-card");
    article.appendChild(el("span", "tag", item.metric));
    article.appendChild(el("h3", "", item.patient_question));
    article.appendChild(el("p", "", item.improvement_signal));
    article.appendChild(el("p", "use", `PFAC use: ${item.pfac_use}`));
    target.appendChild(article);
  }
}

function fillCompetencies(items) {
  const target = document.getElementById("competency-grid");
  target.innerHTML = "";
  for (const item of items) {
    const article = el("article", "card competency-card");
    article.appendChild(el("span", "tag", item.label));
    article.appendChild(el("h3", "", item.agreement_text));
    article.appendChild(el("p", "", item.proof));
    article.appendChild(el("p", "use", `Artifact: ${item.artifact}`));
    target.appendChild(article);
  }
}

function fillSteps(items) {
  const target = document.getElementById("steps");
  target.innerHTML = "";
  for (const item of items) {
    const li = el("li", "step");
    li.appendChild(el("h3", "", item.title));
    li.appendChild(el("p", "", item.leader_action));
    li.appendChild(el("p", "benefit", `Patient benefit: ${item.patient_benefit}`));
    li.appendChild(el("p", "guardrail", `Guardrail: ${item.guardrail}`));
    li.appendChild(el("p", "use", `Artifact: ${item.artifact}`));
    target.appendChild(li);
  }
}

function fillModels(items) {
  const target = document.getElementById("model-grid");
  if (!target) return;
  target.innerHTML = "";
  for (const item of items) {
    const article = el("article", "card model-card");
    article.appendChild(el("span", "tag", item.type));
    article.appendChild(el("h3", "", item.name));
    article.appendChild(el("p", "benefit", `Learn from: ${item.what_to_learn}`));
    article.appendChild(el("p", "guardrail", `Improve on: ${item.how_we_improve}`));
    target.appendChild(article);
  }
}

function fillEvidence(items) {
  const target = document.getElementById("evidence-grid");
  target.innerHTML = "";
  for (const item of items) {
    const article = el("article", "evidence-card");
    article.appendChild(el("span", "tag", item.source));
    article.appendChild(el("h3", "", item.claim));
    article.appendChild(el("p", "benefit", `Patient benefit: ${item.patient_benefit}`));
    article.appendChild(el("p", "guardrail", `Patient risk if ignored: ${item.risk_if_ignored}`));
    article.appendChild(el("p", "use", `Leadership use: ${item.leadership_use}`));
    target.appendChild(article);
  }
}

function fillReferences(items) {
  const target = document.getElementById("references");
  target.innerHTML = "";
  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item;
    target.appendChild(li);
  }
}

function fillOpenResources(items) {
  const target = document.getElementById("open-resources-grid");
  if (!target) return;
  target.innerHTML = "";
  for (const item of items) {
    const article = el("article", "card resource-card");
    article.appendChild(el("span", "tag", item.type));
    article.appendChild(el("h3", "", item.name));
    article.appendChild(el("p", "", item.description));
    article.appendChild(el("p", "benefit", `Research use: ${item.research_use}`));
    const link = el("a", "resource-link", "Open resource");
    link.href = item.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    article.appendChild(link);
    target.appendChild(article);
  }
}

function fillStory(item) {
  if (!item) return;
  const quote = document.getElementById("story-quote");
  const why = document.getElementById("story-why");
  const reason = document.getElementById("story-reason");
  if (quote) quote.textContent = `“${item.approved_excerpt}”`;
  if (why) why.textContent = item.why_it_matters;
  if (reason) reason.textContent = item.why_this_excerpt;
}

function plotTheme() {
  return {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: { color: "#17211f", family: "ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial" },
    margin: { t: 18, r: 18, b: 72, l: 48 },
    xaxis: { zeroline: true, zerolinecolor: "#64736f", gridcolor: "#e4ece8" },
    yaxis: { gridcolor: "#e4ece8" },
    showlegend: false,
  };
}

function fillHaiActions(items) {
  const target = document.getElementById("hai-action-grid");
  if (!target) return;
  target.innerHTML = "";
  for (const item of items) {
    const article = el("article", "action-card");
    article.appendChild(el("span", "tag", item.lane));
    article.appendChild(el("h3", "", item.owner));
    article.appendChild(el("p", "", item.decision));
    target.appendChild(article);
  }
}

function renderHaiCharts(data) {
  const trendTarget = document.getElementById("hai-trend-chart");
  const baselineTarget = document.getElementById("hai-baseline-chart");
  const headline = document.getElementById("hai-headline");
  if (headline) headline.textContent = data.headline;
  fillHaiActions(data.executive_actions || []);
  if (!window.Plotly || !trendTarget || !baselineTarget) return;

  const measures = data.measures || [];
  const labels = measures.map((item) => item.measure);
  const trendValues = measures.map((item) => item.change_vs_2023);
  const baselineValues = measures.map((item) => item.change_vs_2015);
  const colors = trendValues.map((value) => value > 0 ? "#8a3a2b" : "#00693e");
  const hover = measures.map((item) => item.pfac_question);
  const config = { displayModeBar: false, responsive: true };

  Plotly.newPlot(trendTarget, [{
    type: "bar",
    orientation: "h",
    y: labels,
    x: trendValues,
    marker: { color: colors },
    text: trendValues.map((value) => `${value > 0 ? "+" : ""}${value}%`),
    textposition: "auto",
    hovertext: hover,
    hovertemplate: "%{y}: %{x}%<br>%{hovertext}<extra></extra>",
  }], {
    ...plotTheme(),
    xaxis: { ...plotTheme().xaxis, title: "% change vs 2023" },
  }, config);

  Plotly.newPlot(baselineTarget, [{
    type: "scatter",
    mode: "markers+lines",
    x: labels,
    y: baselineValues,
    marker: {
      size: baselineValues.map((value) => Math.max(12, Math.abs(value) * 0.65)),
      color: baselineValues.map((value) => value > 0 ? "#8a3a2b" : "#267aba"),
      line: { color: "#ffffff", width: 2 },
    },
    line: { color: "#9fb2ad", width: 2 },
    text: baselineValues.map((value) => `${value > 0 ? "+" : ""}${value}%`),
    hovertext: hover,
    hovertemplate: "%{x}: %{y}%<br>%{hovertext}<extra></extra>",
  }], {
    ...plotTheme(),
    yaxis: { ...plotTheme().yaxis, title: "% change vs 2015 baseline" },
  }, config);
}

async function boot() {
  const toolkitTarget = document.getElementById("motto");
  const resourcesTarget = document.getElementById("open-resources-grid");
  const haiTarget = document.getElementById("hai-trend-chart");

  if (toolkitTarget) {
    const data = await fetchJson("/api/toolkit");
    toolkitTarget.textContent = data.project.motto;
    fillStory(data.story_anchor);
    fillQuestions(data.project.patient_first_questions);
    fillMetrics(data.metric_drivers);
    fillCompetencies(data.competencies);
    fillSteps(data.playbook_steps);
    fillModels(data.peer_models || []);
    fillEvidence(data.evidence);
    fillReferences(data.references);
    fillOpenResources(data.open_resources || []);
    return;
  }

  if (resourcesTarget) {
    const data = await fetchJson("/api/open-resources");
    fillOpenResources(data.open_resources || []);
  }

  if (haiTarget) {
    const data = await fetchJson("/api/hai-dashboard");
    renderHaiCharts(data);
  }
}

boot().catch((error) => {
  console.error(error);
  document.body.classList.add("load-error");
});
