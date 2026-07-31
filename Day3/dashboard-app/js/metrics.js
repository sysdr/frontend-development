(function () {
  var ENDPOINTS = [
    { name: "cpu", path: "/api/metrics/cpu", metric: "cpu_percent", el: "metric-cpu", fmt: formatPct },
    { name: "memory", path: "/api/metrics/memory", metric: "memory_percent", el: "metric-memory", fmt: formatPct },
    { name: "disk", path: "/api/metrics/disk", metric: "disk_percent", el: "metric-disk", fmt: formatPct },
    { name: "network", path: "/api/metrics/network", metric: "network_mbps", el: "metric-network", fmt: formatMbps }
  ];

  function formatPct(n) {
    return Number(n).toFixed(1) + "%";
  }

  function formatMbps(n) {
    return Number(n).toFixed(1) + " Mbps";
  }

  function detectMode() {
    var grid = document.querySelector(".metrics-grid");
    if (grid && grid.getAttribute("data-fetch-mode") === "sequential") {
      return "sequential";
    }
    return "parallel";
  }

  async function timedFetch(endpoint) {
    var start = performance.now();
    var res = await fetch(endpoint.path, { cache: "no-store" });
    if (!res.ok) throw new Error(endpoint.path + " HTTP " + res.status);
    var data = await res.json();
    var end = performance.now();
    return {
      name: endpoint.name,
      start: start,
      end: end,
      duration: end - start,
      value: data[endpoint.metric],
      updated_at: data.updated_at,
      demo_runs: data.demo_runs,
      endpoint: endpoint
    };
  }

  function applyResults(results) {
    results.forEach(function (r) {
      var node = document.getElementById(r.endpoint.el);
      if (node) node.textContent = r.endpoint.fmt(r.value);
    });
    var status = document.getElementById("status-line");
    if (status && results.length) {
      var last = results[results.length - 1];
      status.textContent =
        "Updated " + (last.updated_at || "—") +
        " · demo_runs=" + (last.demo_runs || 0) +
        " · mode=" + detectMode();
    }
    if (window.renderNetworkWaterfall) {
      window.renderNetworkWaterfall(results.map(function (r) {
        return { name: r.name, start: r.start, end: r.end, duration: r.duration };
      }));
    }
  }

  async function refreshSequential() {
    var results = [];
    for (var i = 0; i < ENDPOINTS.length; i++) {
      results.push(await timedFetch(ENDPOINTS[i]));
    }
    applyResults(results);
    return results;
  }

  async function refreshParallel() {
    var results = await Promise.all(ENDPOINTS.map(timedFetch));
    applyResults(results);
    return results;
  }

  async function refreshMetrics() {
    try {
      if (detectMode() === "sequential") {
        return await refreshSequential();
      }
      return await refreshParallel();
    } catch (err) {
      console.warn("metrics refresh failed:", err);
      var status = document.getElementById("status-line");
      if (status) status.textContent = "Metrics refresh failed: " + err.message;
    }
  }

  window.refreshDashboardMetrics = refreshMetrics;
  window.__METRIC_ENDPOINTS__ = ENDPOINTS;

  var refreshBtn = document.getElementById("btn-refresh");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", async function () {
      refreshBtn.disabled = true;
      try {
        await refreshMetrics();
      } finally {
        refreshBtn.disabled = false;
      }
    });
  }

  refreshMetrics();
  setInterval(refreshMetrics, 2500);
})();
