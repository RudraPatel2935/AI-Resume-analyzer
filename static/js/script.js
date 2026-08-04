document.addEventListener("DOMContentLoaded", () => {
  const animatedBlocks = document.querySelectorAll(".mini-card, .panel-card, .stat-card, .hero-stat, .auth-panel, .feature-panel");
  animatedBlocks.forEach((block, index) => {
    block.style.opacity = "0";
    block.style.transform = "translateY(12px)";
    block.style.transition = "opacity 420ms ease, transform 420ms ease";
    window.setTimeout(() => {
      block.style.opacity = "1";
      block.style.transform = "translateY(0)";
    }, 70 * index);
  });

  const canvas = document.getElementById("atsChart");
  if (!canvas || typeof window.aiCareerStats === "undefined") {
    return;
  }

  const ctx = canvas.getContext("2d");
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Match", "Gap"],
      datasets: [{
        data: [window.aiCareerStats, Math.max(0, 100 - window.aiCareerStats)],
        backgroundColor: ["#0ea5e9", "#e2e8f0"],
      }],
    },
    options: { responsive: true, plugins: { legend: { position: "bottom" } } },
  });
});