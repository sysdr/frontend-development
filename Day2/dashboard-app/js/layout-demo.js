(function () {
  const grid = document.querySelector(".metrics-grid");
  if (!grid) return;
  const mode = grid.getAttribute("data-layout") || "unknown";
  document.documentElement.setAttribute("data-layout-mode", mode);
  // Subtle presence motion on fixed layout only
  if (mode === "fixed") {
    grid.querySelectorAll(".metric-card").forEach(function (card, i) {
      card.style.animation = "fadeRise 0.45s ease " + (i * 0.06) + "s both";
    });
    const style = document.createElement("style");
    style.textContent =
      "@keyframes fadeRise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}";
    document.head.appendChild(style);
  }
})();
