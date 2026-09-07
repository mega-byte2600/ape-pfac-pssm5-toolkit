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

function card(title, body, eyebrow) {
  const article = el("article", "card");
  if (eyebrow) article.appendChild(el("span", "tag", eyebrow));
  article.appendChild(el("h3", "", title));
  article.appendChild(el("p", "", body));
  return article;
}

function fillQuestions(items) {
  const target = document.getElementById("questions");
  target.innerHTML = "";
  for (const item of items) {
    const div = el("div", "question", item);
    target.appendChild(div);
  }
}

function fillMetrics(items) {
  const target = document.getElementById("metric-grid");
  target.innerHTML = "";
  for (const item of items) {
    const article = el("article", "card metric-card");
    article.appendChild(el("span", "tag", item.metric));
    article.appendChild(el("h3", "", item.patient_question));
    article.appendChild(el("p", "", item.improvement_signal));
    const use = el("p", "use", `PFAC use: ${item.pfac_use}`);
    article.appendChild(use);
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

async function boot() {
  const data = await fetchJson("/api/toolkit");
  document.getElementById("motto").textContent = data.project.motto;
  fillQuestions(data.project.patient_first_questions);
  fillMetrics(data.metric_drivers);
  fillCompetencies(data.competencies);
  fillSteps(data.playbook_steps);
  fillEvidence(data.evidence);
  fillReferences(data.references);
  fillOpenResources(data.open_resources || []);
}

boot().catch((error) => {
  console.error(error);
  document.body.classList.add("load-error");
});
