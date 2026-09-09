(function () {
  const steps = [
    { label: "Start", href: "/" },
    { label: "Reviewer Guide", href: "/mvp-one.html" },
    { label: "Evidence", href: "/evidence-summary.html" },
    { label: "Benchmark", href: "/dh-benchmark.html" },
    { label: "Analysis", href: "/applied-analysis.html" },
    { label: "Tools", href: "/toolkit-tools.html" },
    { label: "About", href: "/about.html" },
  ];

  function normalizedPath() {
    const path = window.location.pathname;
    return path === "/index.html" ? "/" : path;
  }

  function mountReviewFlow() {
    if (document.querySelector("[data-review-flow]")) {
      return;
    }

    const header = document.querySelector(".site-header");
    if (!header) {
      return;
    }

    const current = normalizedPath();
    const nav = document.createElement("nav");
    nav.className = "review-flow";
    nav.setAttribute("aria-label", "Reviewer flow");
    nav.setAttribute("data-review-flow", "");

    steps.forEach((step, index) => {
      const link = document.createElement("a");
      link.href = step.href;
      link.textContent = step.label;
      link.dataset.step = String(index + 1);
      if (step.href === current) {
        link.setAttribute("aria-current", "page");
      }
      nav.appendChild(link);
    });

    header.insertAdjacentElement("afterend", nav);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountReviewFlow);
  } else {
    mountReviewFlow();
  }
})();
