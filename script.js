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
const budgetStateNames = {
  CA: "California",
  CO: "Colorado",
  PA: "Pennsylvania",
  WA: "Washington",
  WI: "Wisconsin",
};
const taxBracketCache = new Map();

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(value);
}

function parseTaxCsv(text) {
  const lines = text.trim().split(/\r?\n/).slice(1);
  return lines
    .map((line) => line.split(","))
    .filter((parts) => parts.length >= 3)
    .map(([min, max, rate]) => ({
      min: Number(min),
      max: max.trim().toLowerCase() === "inf" ? Number.POSITIVE_INFINITY : Number(max),
      rate: Number(rate),
    }));
}

async function loadTaxBrackets(csvPath) {
  if (taxBracketCache.has(csvPath)) {
    return taxBracketCache.get(csvPath);
  }

  const response = await fetch(csvPath);
  if (!response.ok) {
    throw new Error(`Unable to load tax data from ${csvPath}.`);
  }

  const brackets = parseTaxCsv(await response.text());
  taxBracketCache.set(csvPath, brackets);
  return brackets;
}

function calcTax(income, brackets) {
  let tax = 0;
  for (const row of brackets) {
    if (income <= row.min) {
      break;
    }
    const taxable = Math.min(income, row.max) - row.min;
    tax += taxable * row.rate;
  }
  return tax;
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

    const taxDir = budgetForm.dataset.taxDir || "../project-files/budget-scripts";
    const federalPath = new URL(`${taxDir}/federal.csv`, window.location.href).href;
    const statePath = new URL(
      `${taxDir}/${budgetStateNames[payload.state_code].toLowerCase()}.csv`,
      window.location.href
    ).href;

    budgetStatus.textContent = "Calculating...";
    budgetResults.hidden = true;

    try {
      if (!budgetStateNames[payload.state_code]) {
        throw new Error("Unsupported state selection.");
      }
      if (payload.gross_income <= 0) {
        throw new Error("Gross income must be greater than 0.");
      }
      if (payload.pretax_401k_percent < 0 || payload.pretax_401k_percent > 100) {
        throw new Error("401(k) percent must be between 0 and 100.");
      }

      const [federalBrackets, stateBrackets] = await Promise.all([
        loadTaxBrackets(federalPath),
        loadTaxBrackets(statePath),
      ]);

      const pretax401k = payload.gross_income * (payload.pretax_401k_percent / 100);
      const taxableIncome = Math.max(payload.gross_income - pretax401k, 0);
      const federalTax = calcTax(taxableIncome, federalBrackets);
      const stateTax = calcTax(taxableIncome, stateBrackets);
      const netIncome = payload.gross_income - pretax401k - federalTax - stateTax;
      const monthlyNetIncome = netIncome / 12;

      budgetResults.querySelector('[data-result="state_name"]').textContent =
        budgetStateNames[payload.state_code];
      budgetResults.querySelector('[data-result="federal_tax"]').textContent =
        formatCurrency(federalTax);
      budgetResults.querySelector('[data-result="state_tax"]').textContent =
        formatCurrency(stateTax);
      budgetResults.querySelector('[data-result="net_income"]').textContent =
        formatCurrency(netIncome);
      budgetResults.querySelector('[data-result="monthly_net_income"]').textContent =
        formatCurrency(monthlyNetIncome);
      budgetResults.querySelector('[data-result="pretax_401k"]').textContent =
        formatCurrency(pretax401k);

      budgetStatus.textContent = "";
      budgetResults.hidden = false;
    } catch (error) {
      budgetStatus.textContent = error instanceof Error ? error.message : "Unable to calculate summary.";
      budgetResults.hidden = true;
    }
  });
}
