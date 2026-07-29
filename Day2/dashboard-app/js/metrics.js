(function () {
  function formatPct(n) {
    return Number(n).toFixed(1) + "%";
  }

  function formatMbps(n) {
    return Number(n).toFixed(1) + " Mbps";
  }

  async function refreshMetrics() {
    try {
      const res = await fetch("/api/metrics", { cache: "no-store" });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      const cpu = document.getElementById("metric-cpu");
      const memory = document.getElementById("metric-memory");
      const disk = document.getElementById("metric-disk");
      const network = document.getElementById("metric-network");
      if (cpu) cpu.textContent = formatPct(data.cpu_percent);
      if (memory) memory.textContent = formatPct(data.memory_percent);
      if (disk) disk.textContent = formatPct(data.disk_percent);
      if (network) network.textContent = formatMbps(data.network_mbps);
      const status = document.getElementById("status-line");
      if (status) {
        status.textContent =
          "Updated " + (data.updated_at || "—") +
          " · demo_runs=" + (data.demo_runs || 0);
      }
    } catch (err) {
      console.warn("metrics refresh failed:", err);
    }
  }

  window.refreshDashboardMetrics = refreshMetrics;
  refreshMetrics();
  setInterval(refreshMetrics, 1500);
})();
