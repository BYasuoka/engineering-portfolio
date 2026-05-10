import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
TAX_DIR = BASE_DIR / "project-files" / "budget-scripts"
FEDERAL_CSV = TAX_DIR / "federal.csv"
STATE_FILES = {
    "CA": TAX_DIR / "california.csv",
    "CO": TAX_DIR / "colorado.csv",
    "PA": TAX_DIR / "pennsylvania.csv",
    "WA": TAX_DIR / "washington.csv",
    "WI": TAX_DIR / "wisconsin.csv",
}
STATE_LABELS = {
    "CA": "California",
    "CO": "Colorado",
    "PA": "Pennsylvania",
    "WA": "Washington",
    "WI": "Wisconsin",
}


def load_tax_brackets(path: Path) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    with path.open(newline="") as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
          upper_text = row["max"].strip().lower()
          upper = float("inf") if upper_text == "inf" else float(row["max"])
          rows.append(
              {
                  "min": float(row["min"]),
                  "max": upper,
                  "rate": float(row["rate"]),
              }
          )
    return rows


FEDERAL_BRACKETS = load_tax_brackets(FEDERAL_CSV)
STATE_BRACKETS = {key: load_tax_brackets(path) for key, path in STATE_FILES.items()}


def calc_tax(income: float, brackets: list[dict[str, float]]) -> float:
    tax = 0.0
    for row in brackets:
        lower = row["min"]
        upper = row["max"]
        rate = row["rate"]
        if income <= lower:
            break
        taxable = min(income, upper) - lower
        tax += taxable * rate
    return tax


def summarize_budget_inputs(
    gross_income: float,
    state_code: str,
    pretax_401k_percent: float = 0.0,
) -> dict[str, float | str]:
    state_code = state_code.upper()
    if state_code not in STATE_BRACKETS:
        raise ValueError("Unsupported state selection.")
    if gross_income <= 0:
        raise ValueError("Gross income must be greater than 0.")
    if pretax_401k_percent < 0 or pretax_401k_percent > 100:
        raise ValueError("401(k) percent must be between 0 and 100.")

    annual_401k = gross_income * (pretax_401k_percent / 100.0)
    taxable_income = max(gross_income - annual_401k, 0.0)
    federal_tax = calc_tax(taxable_income, FEDERAL_BRACKETS)
    state_tax = calc_tax(taxable_income, STATE_BRACKETS[state_code])
    net_income = gross_income - annual_401k - federal_tax - state_tax

    return {
        "state_code": state_code,
        "state_name": STATE_LABELS[state_code],
        "gross_income": gross_income,
        "pretax_401k": annual_401k,
        "taxable_income": taxable_income,
        "federal_tax": federal_tax,
        "state_tax": state_tax,
        "net_income": net_income,
        "monthly_net_income": net_income / 12.0,
    }
