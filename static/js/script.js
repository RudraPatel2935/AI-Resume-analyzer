// Theme Switcher Logic
(function initTheme() {
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    document.documentElement.setAttribute("data-theme", savedTheme);
  } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    document.documentElement.setAttribute("data-theme", "dark");
  }
})();

document.addEventListener("DOMContentLoaded", () => {
  // Theme Toggle Button Setup
  const themeToggleBtn = document.getElementById("themeToggleBtn");
  const themeIcon = document.getElementById("themeIcon");
  const themeLabel = document.getElementById("themeLabel");

  function updateThemeUI(theme) {
    if (theme === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
      localStorage.setItem("theme", "dark");
      if (themeIcon) themeIcon.textContent = "☀️";
      if (themeLabel) themeLabel.textContent = "Light";
    } else {
      document.documentElement.setAttribute("data-theme", "light");
      localStorage.setItem("theme", "light");
      if (themeIcon) themeIcon.textContent = "🌙";
      if (themeLabel) themeLabel.textContent = "Dark";
    }
  }

  const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
  updateThemeUI(currentTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      const activeTheme = document.documentElement.getAttribute("data-theme");
      const nextTheme = activeTheme === "dark" ? "light" : "dark";
      updateThemeUI(nextTheme);
    });
  }

  // Animation Blocks
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

  // Chart.js ATS chart
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