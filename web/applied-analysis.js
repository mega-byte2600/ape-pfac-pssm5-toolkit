(() => {
  const root = document.querySelector('[data-local-analysis]');
  if (!root) return;

  const metricSelect = root.querySelector('#analysis-metric');
  const thresholdSelect = root.querySelector('#analysis-threshold');
  const sortSelect = root.querySelector('#analysis-sort');
  const searchInput = root.querySelector('#analysis-search');
  const tableBody = root.querySelector('#analysis-body');
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

    status.textContent = visible.length ? `${visible.length} municipalities shown.` : 'No municipalities match the current filters.';
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
      status.textContent = 'Interactive table unavailable. The validated calculation file remains available below.';
      tableBody.innerHTML = '<tr><td colspan="5">Unable to load the local calculation file.</td></tr>';
    });
})();
