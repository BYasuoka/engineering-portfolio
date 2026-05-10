const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector(".site-nav");

if (menuToggle && siteNav) {
  menuToggle.addEventListener("click", () => {
    const isOpen = siteNav.classList.toggle("is-open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
  });

  siteNav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      siteNav.classList.remove("is-open");
      menuToggle.setAttribute("aria-expanded", "false");
    });
  });
}

const budgetForm = document.querySelector("[data-budget-form]");
const budgetStatus = document.querySelector("[data-budget-status]");
const budgetResults = document.querySelector("[data-budget-results]");

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(value);
}

if (budgetForm && budgetStatus && budgetResults) {
  budgetForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(budgetForm);
    const payload = {
      gross_income: Number(formData.get("gross_income")),
      state_code: String(formData.get("state_code")),
      pretax_401k_percent: Number(formData.get("pretax_401k_percent") || 0),
    };

    budgetStatus.textContent = "Calculating...";
    budgetResults.hidden = true;

    try {
      const response = await fetch("/api/budget-summary", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const contentType = response.headers.get("content-type") || "";
      if (!contentType.includes("application/json")) {
        throw new Error(
          "Budget API unavailable. Start the site with `python3 server.py` instead of a static server."
        );
      }

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Request failed.");
      }

      budgetResults.querySelector('[data-result="state_name"]').textContent = data.state_name;
      budgetResults.querySelector('[data-result="federal_tax"]').textContent = formatCurrency(data.federal_tax);
      budgetResults.querySelector('[data-result="state_tax"]').textContent = formatCurrency(data.state_tax);
      budgetResults.querySelector('[data-result="net_income"]').textContent = formatCurrency(data.net_income);
      budgetResults.querySelector('[data-result="monthly_net_income"]').textContent = formatCurrency(data.monthly_net_income);
      budgetResults.querySelector('[data-result="pretax_401k"]').textContent = formatCurrency(data.pretax_401k);

      budgetStatus.textContent = "";
      budgetResults.hidden = false;
    } catch (error) {
      budgetStatus.textContent = error instanceof Error ? error.message : "Unable to calculate summary.";
      budgetResults.hidden = true;
    }
  });
}
