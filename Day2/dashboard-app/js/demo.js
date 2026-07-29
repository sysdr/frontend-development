/**
 * Client-side helper used by scripts/demo.sh via the API.
 * Kept for documentation / browser console demos.
 */
async function runClientDemo() {
  const res = await fetch("/api/demo", { method: "POST" });
  const data = await res.json();
  if (window.refreshDashboardMetrics) await window.refreshDashboardMetrics();
  return data;
}
window.runClientDemo = runClientDemo;
