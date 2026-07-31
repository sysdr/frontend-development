(function () {
  function renderWaterfall(entries) {
    const root = document.getElementById("waterfall");
    const summary = document.getElementById("waterfall-summary");
    if (!root) return;

    root.innerHTML = "";
    if (!entries || !entries.length) {
      if (summary) summary.textContent = "No fetches yet.";
      return;
    }

    const t0 = Math.min.apply(null, entries.map(function (e) { return e.start; }));
    const t1 = Math.max.apply(null, entries.map(function (e) { return e.end; }));
    const span = Math.max(1, t1 - t0);

    entries.forEach(function (entry) {
      const row = document.createElement("div");
      row.className = "waterfall-row";

      const label = document.createElement("div");
      label.className = "waterfall-label";
      label.textContent = entry.name;

      const track = document.createElement("div");
      track.className = "waterfall-track";
      const bar = document.createElement("div");
      bar.className = "waterfall-bar";
      bar.setAttribute("data-name", entry.name);
      const leftPct = ((entry.start - t0) / span) * 100;
      const widthPct = Math.max(1.5, ((entry.end - entry.start) / span) * 100);
      bar.style.left = leftPct.toFixed(2) + "%";
      bar.style.width = widthPct.toFixed(2) + "%";
      bar.title = entry.name + ": " + entry.duration.toFixed(0) + " ms";
      track.appendChild(bar);

      const ms = document.createElement("div");
      ms.className = "waterfall-ms";
      ms.textContent = entry.duration.toFixed(0) + " ms";

      row.appendChild(label);
      row.appendChild(track);
      row.appendChild(ms);
      root.appendChild(row);
    });

    const wall = t1 - t0;
    const sum = entries.reduce(function (acc, e) { return acc + e.duration; }, 0);
    if (summary) {
      summary.textContent =
        "Wall clock " + wall.toFixed(0) + " ms · sum of requests " +
        sum.toFixed(0) + " ms · " + entries.length + " endpoints";
    }
  }

  window.renderNetworkWaterfall = renderWaterfall;
})();
