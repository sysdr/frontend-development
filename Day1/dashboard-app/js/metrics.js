(function () {
  function formatRevenue(n) {
    return "$" + Number(n).toLocaleString("en-US");
  }

  function formatInt(n) {
    return Number(n).toLocaleString("en-US");
  }

  async function refreshMetrics() {
    try {
      const res = await fetch("/api/metrics", { cache: "no-store" });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      const users = document.getElementById("metric-users");
      const sessions = document.getElementById("metric-sessions");
      const revenue = document.getElementById("metric-revenue");
      if (users) users.textContent = formatInt(data.total_users);
      if (sessions) sessions.textContent = formatInt(data.active_sessions);
      if (revenue) revenue.textContent = formatRevenue(data.revenue_ytd);
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
