(function () {
  const toolSelect = document.querySelector("#leadership-tool-select");
  const focusSelect = document.querySelector("#leadership-focus-select");
  const focusWrap = document.querySelector("#leadership-focus-wrap");
  const summary = document.querySelector("#leadership-tool-summary");
  const panels = Array.from(document.querySelectorAll("[data-leadership-tool]"));

  if (!toolSelect || !focusSelect || !focusWrap || !summary || !panels.length) {
    return;
  }

  document.body.classList.add("leadership-tools-enhanced");

  function panelFor(value) {
    return panels.find((panel) => panel.dataset.leadershipTool === value);
  }

  function tableRows(panel) {
    const table = panel.querySelector("table");
    if (!table) return [];

    const headers = Array.from(table.querySelectorAll("thead th")).map((cell) => cell.textContent.trim());
    return Array.from(table.querySelectorAll("tbody tr")).map((row) => {
      const cells = Array.from(row.querySelectorAll("td")).map((cell) => cell.textContent.trim());
      const label = row.dataset.focusLabel || cells[0] || "Selected view";
      return { headers, cells, label };
    });
  }

  function clearSummary() {
    summary.replaceChildren();
  }

  function renderRow(row) {
    clearSummary();
    if (!row || !row.cells.length) return;

    const heading = document.createElement("h3");
    heading.textContent = row.label;
    summary.appendChild(heading);

    const grid = document.createElement("div");
    grid.className = "tool-summary-grid";

    row.headers.slice(1).forEach((header, index) => {
      const value = row.cells[index + 1];
      if (!value) return;

      const item = document.createElement("article");
      item.className = "tool-summary-item";
      const label = document.createElement("span");
      label.textContent = header;
      const text = document.createElement("p");
      text.textContent = value;
      item.append(label, text);
      grid.appendChild(item);
    });

    if (grid.children.length) {
      summary.appendChild(grid);
    }
  }

  function populateFocus(panel) {
    const rows = tableRows(panel);
    focusSelect.replaceChildren();

    if (!rows.length) {
      focusWrap.hidden = true;
      clearSummary();
      return;
    }

    focusWrap.hidden = false;
    rows.forEach((row, index) => {
      const option = document.createElement("option");
      option.value = String(index);
      option.textContent = row.label;
      focusSelect.appendChild(option);
    });

    renderRow(rows[0]);
  }

  function activateTool(value, updateHash) {
    const active = panelFor(value) || panels[0];
    toolSelect.value = active.dataset.leadershipTool;

    panels.forEach((panel) => {
      panel.hidden = panel !== active;
    });

    populateFocus(active);
    if (updateHash) {
      history.replaceState(null, "", `#${active.id}`);
    }
  }

  toolSelect.addEventListener("change", () => activateTool(toolSelect.value, true));

  focusSelect.addEventListener("change", () => {
    const panel = panelFor(toolSelect.value);
    const rows = panel ? tableRows(panel) : [];
    renderRow(rows[Number(focusSelect.value)]);
  });

  document.addEventListener("click", (event) => {
    const link = event.target.closest('a[href^="#"]');
    if (!link) return;
    const id = link.getAttribute("href").slice(1);
    const panel = panels.find((item) => item.id === id);
    if (!panel) return;
    activateTool(panel.dataset.leadershipTool, false);
  });

  const initialId = window.location.hash.slice(1);
  const initialPanel = panels.find((panel) => panel.id === initialId);
  activateTool(initialPanel ? initialPanel.dataset.leadershipTool : toolSelect.value, false);
})();
