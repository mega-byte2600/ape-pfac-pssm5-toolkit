(() => {
  const root = document.querySelector('[data-local-analysis]');
  if (!root) return;

  const metricSelect = root.querySelector('#analysis-metric');
  const thresholdSelect = root.querySelector('#analysis-threshold');
  const sortSelect = root.querySelector('#analysis-sort');
  const searchInput = root.querySelector('#analysis-search');
  const tableBody = root.querySelector('#analysis-body');
  const chartTarget = root.querySelector('#analysis-chart');
  const chartTitle = root.querySelector('#analysis-chart-title');
  const resultCount = root.querySelector('#analysis-result-count');
  const populationShown = root.querySelector('#analysis-population-shown');
  const aboveShare = root.querySelector('#analysis-above-share');
  const aboveCount = root.querySelector('#analysis-above-count');
  const readout = root.querySelector('#analysis-readout');
  const status = root.querySelector('#analysis-status');

  const METRICS = {
    poverty: {
      label: 'Poverty',
      field: 'Poverty percent',
      flag: 'Above service-area poverty average (8%)',
      benchmark: 8,
      implication: 'Recruitment and participation should account for cost, compensation, transportation, time, and other economic barriers.'
    },
    disability: {
      label: 'Disability',
      field: 'Disability percent',
      flag: 'Above service-area disability average (12%)',
      benchmark: 12,
      implication: 'Accessible formats, communication options, remote participation, caregiver input, and disability access should be core operating requirements.'
    },
    age65: {
      label: 'Age 65+',
      field: 'Age 65+ percent',
      flag: 'Above service-area age 65+ average (22%)',
      benchmark: 22,
      implication: 'Older-adult and caregiver perspectives should be intentionally reachable, especially where transportation, isolation, technology, and aging-in-place barriers overlap.'
    }
  };

  const parseCsv = (text) => {
    const lines = text.trim().split(/\r?\n/);
    const headers = lines[0].split(',');
    return lines.slice(1).map((line) => {
      const values = line.split(',');
      return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? '']));
    });
  };

  const number = (value) => Number.parseFloat(value) || 0;
  const integer = (value) => Number.parseInt(value, 10) || 0;
  const fmt = new Intl.NumberFormat('en-US');
  let rows = [];

  function renderChart(visible, metric) {
    if (!chartTarget || !window.Plotly) return;
    chartTitle.textContent = `${metric.label} by municipality`;

    if (!visible.length) {
      Plotly.react(chartTarget, [], {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        annotations: [{ text: 'No municipalities match the current filters.', showarrow: false, x: 0.5, y: 0.5, xref: 'paper', yref: 'paper' }],
        margin: { t: 20, r: 20, b: 45, l: 20 }
      }, { displayModeBar: false, responsive: true });
      return;
    }

    const chartRows = [...visible].reverse();
    const values = chartRows.map((row) => number(row[metric.field]));
    const names = chartRows.map((row) => row.Municipality);
    const populations = chartRows.map((row) => fmt.format(integer(row['2023 population'])));
    const comparisons = chartRows.map((row) => row[metric.flag] === 'Yes' ? 'Above service-area average' : 'At or below service-area average');

    Plotly.react(chartTarget, [{
      type: 'bar',
      orientation: 'h',
      y: names,
      x: values,
      marker: { color: chartRows.map((row) => row[metric.flag] === 'Yes' ? '#c49a3a' : '#00693e') },
      customdata: populations.map((population, index) => [population, comparisons[index]]),
      hovertemplate: '<b>%{y}</b><br>' + metric.label + ': %{x}%<br>Population: %{customdata[0]}<br>%{customdata[1]}<extra></extra>'
    }], {
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: { color: '#17211f', family: 'ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial' },
      margin: { t: 24, r: 30, b: 60, l: 115 },
      xaxis: { title: `${metric.label} percent`, gridcolor: '#e4ece8', rangemode: 'tozero', ticksuffix: '%' },
      yaxis: { automargin: true },
      shapes: [{ type: 'line', x0: metric.benchmark, x1: metric.benchmark, y0: -0.5, y1: chartRows.length - 0.5, line: { color: '#8a3a2b', width: 2, dash: 'dash' } }],
      annotations: [{ x: metric.benchmark, y: 1.04, xref: 'x', yref: 'paper', text: `Service-area average ${metric.benchmark}%`, showarrow: false, font: { color: '#8a3a2b', size: 12 } }],
      showlegend: false
    }, { displayModeBar: false, responsive: true });
  }

  function render() {
    const metric = METRICS[metricSelect.value];
    const query = searchInput.value.trim().toLowerCase();
    const threshold = thresholdSelect.value;

    let visible = rows.filter((row) => {
      const matchesTown = !query || row.Municipality.toLowerCase().includes(query);
      const isAbove = row[metric.flag] === 'Yes';
      const matchesThreshold = threshold === 'all' || (threshold === 'above' && isAbove) || (threshold === 'not-above' && !isAbove);
      return matchesTown && matchesThreshold;
    });

    visible = [...visible].sort((a, b) => {
      switch (sortSelect.value) {
        case 'town':
          return a.Municipality.localeCompare(b.Municipality);
        case 'metric-desc':
          return number(b[metric.field]) - number(a[metric.field]) || a.Municipality.localeCompare(b.Municipality);
        case 'metric-asc':
          return number(a[metric.field]) - number(b[metric.field]) || a.Municipality.localeCompare(b.Municipality);
        default:
          return integer(b['2023 population']) - integer(a['2023 population']) || a.Municipality.localeCompare(b.Municipality);
      }
    });

    const totalPopulation = rows.reduce((sum, row) => sum + integer(row['2023 population']), 0);
    const aboveRows = rows.filter((row) => row[metric.flag] === 'Yes');
    const abovePopulation = aboveRows.reduce((sum, row) => sum + integer(row['2023 population']), 0);
    const shownPopulation = visible.reduce((sum, row) => sum + integer(row['2023 population']), 0);
    const share = totalPopulation ? (abovePopulation / totalPopulation) * 100 : 0;

    resultCount.textContent = `${visible.length} of ${rows.length}`;
    populationShown.textContent = fmt.format(shownPopulation);
    aboveShare.textContent = `${share.toFixed(1)}%`;
    aboveCount.textContent = `${aboveRows.length} towns`;

    readout.innerHTML = `<strong>${metric.label}:</strong> ${share.toFixed(1)}% of the ${fmt.format(totalPopulation)} service-area residents live in ${aboveRows.length} municipalities where the published ${metric.label.toLowerCase()} percentage is above the ${metric.benchmark}% service-area average. ${metric.implication}`;

    renderChart(visible, metric);

    tableBody.innerHTML = visible.map((row) => {
      const isAbove = row[metric.flag] === 'Yes';
      return `<tr>
        <td><strong>${row.Municipality}</strong></td>
        <td>${fmt.format(integer(row['2023 population']))}</td>
        <td>${number(row[metric.field]).toFixed(0)}%</td>
        <td>${metric.benchmark}%</td>
        <td><span class="status-pill${isAbove ? ' above' : ''}">${isAbove ? 'Above service-area average' : 'At or below service-area average'}</span></td>
      </tr>`;
    }).join('');

    status.textContent = visible.length ? `${visible.length} municipalities shown in the chart and supporting table.` : 'No municipalities match the current filters.';
  }

  [metricSelect, thresholdSelect, sortSelect].forEach((control) => control.addEventListener('change', render));
  searchInput.addEventListener('input', render);

  fetch('/upper-valley-local-analysis.csv', { cache: 'no-store' })
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.text();
    })
    .then((text) => {
      rows = parseCsv(text);
      render();
    })
    .catch(() => {
      status.textContent = 'Interactive analysis unavailable. The validated calculation file remains available below.';
      tableBody.innerHTML = '<tr><td colspan="5">Unable to load the local calculation file.</td></tr>';
    });
})();
