import csv
from pathlib import Path

import matplotlib.pyplot as plt


BASE_DIR = Path("/Users/hoodieb/Documents/VSCODE/Budget_scripts/")
FEDERAL_CSV = BASE_DIR / "federal.csv"
WISCONSIN_CSV = BASE_DIR / "wisconsin.csv"
STATE_NAME = "Wisconsin"
PAY_PERIODS_PER_YEAR = 12


def load_tax_brackets(path):
    rows = []

    with path.open(newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames or []

        required_columns = {"min", "max", "rate"}
        if not required_columns.issubset(fieldnames):
            raise ValueError(
                f"{path.name} must contain the columns: min, max, rate."
            )

        for row in reader:
            upper_value = row["max"].strip().lower()
            upper = float("inf") if upper_value == "inf" else float(row["max"])
            rows.append(
                {
                    "min": float(row["min"]),
                    "max": upper,
                    "rate": float(row["rate"]),
                }
            )

    if not rows:
        raise ValueError(
            f"{path.name} is empty. Add Wisconsin tax brackets before running this script."
        )

    return rows


def calc_tax(income, brackets):
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


def calc_net_income(gross_income, federal_brackets, state_brackets, pretax_deduction=0):
    taxable_income = max(gross_income - pretax_deduction, 0)
    fed_tax = calc_tax(taxable_income, federal_brackets)
    state_tax = calc_tax(taxable_income, state_brackets)
    return gross_income - pretax_deduction - fed_tax - state_tax


def build_scenario_data(gross_income, federal_brackets, state_brackets, roth_annual_limit):
    monthly_roth = roth_annual_limit / PAY_PERIODS_PER_YEAR
    annual_401k = gross_income * 0.08

    net_no_retirement = calc_net_income(gross_income, federal_brackets, state_brackets)
    net_401k_only = calc_net_income(
        gross_income, federal_brackets, state_brackets, annual_401k
    )
    net_roth_only = net_no_retirement - roth_annual_limit
    net_both = net_401k_only - roth_annual_limit

    return [
        {
            "name": "No retirement contributions",
            "monthly_401k": 0.0,
            "monthly_roth": 0.0,
            "monthly_net": net_no_retirement / PAY_PERIODS_PER_YEAR,
        },
        {
            "name": "8% 401(k) only",
            "monthly_401k": annual_401k / PAY_PERIODS_PER_YEAR,
            "monthly_roth": 0.0,
            "monthly_net": net_401k_only / PAY_PERIODS_PER_YEAR,
        },
        {
            "name": "Roth IRA only",
            "monthly_401k": 0.0,
            "monthly_roth": monthly_roth,
            "monthly_net": net_roth_only / PAY_PERIODS_PER_YEAR,
        },
        {
            "name": "8% 401(k) + Roth IRA",
            "monthly_401k": annual_401k / PAY_PERIODS_PER_YEAR,
            "monthly_roth": monthly_roth,
            "monthly_net": net_both / PAY_PERIODS_PER_YEAR,
        },
    ]


def format_currency(amount):
    return f"${amount:,.2f}"


def build_summary_rows(gross_income, federal_tax, state_tax, net_income):
    return [
        ["State", STATE_NAME],
        ["Gross income", format_currency(gross_income)],
        ["Federal tax", format_currency(federal_tax)],
        ["State tax", format_currency(state_tax)],
        ["Net income before retirement", format_currency(net_income)],
    ]


def build_scenario_rows(scenarios):
    rows = []
    for scenario in scenarios:
        rows.append(
            [
                scenario["name"],
                format_currency(scenario["monthly_401k"]),
                format_currency(scenario["monthly_roth"]),
                format_currency(scenario["monthly_net"]),
            ]
        )
    return rows


def build_budget_rows(scenarios):
    budget_splits = [
        ("50/30/20", 0.50, 0.30, 0.20),
        ("60/20/20", 0.60, 0.20, 0.20),
        ("60/10/30", 0.60, 0.10, 0.30),
    ]

    rows = []
    for scenario in scenarios:
        monthly_net = scenario["monthly_net"]
        for label, needs_pct, wants_pct, savings_pct in budget_splits:
            rows.append(
                [
                    scenario["name"],
                    label,
                    format_currency(monthly_net * needs_pct),
                    format_currency(monthly_net * wants_pct),
                    format_currency(monthly_net * savings_pct),
                ]
            )
    return rows


def style_table(table, header_color, label_columns=None):
    label_columns = label_columns or set()
    table.auto_set_font_size(False)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("black")
        cell.set_linewidth(1.0)

        if row == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(weight="bold", color="white")
        elif col in label_columns:
            cell.set_facecolor("#e8eef5")
            cell.set_text_props(weight="bold")
        else:
            cell.set_facecolor("#f7f7f7")


def show_tables(gross_income, federal_tax, state_tax, net_income, scenarios):
    fig, axes = plt.subplots(
        3,
        1,
        figsize=(14, 12),
        gridspec_kw={"height_ratios": [1.0, 1.35, 2.2]},
    )

    summary_ax, scenario_ax, budget_ax = axes

    for ax in axes:
        ax.axis("off")

    summary_table = summary_ax.table(
        cellText=build_summary_rows(gross_income, federal_tax, state_tax, net_income),
        colLabels=["Category", "Amount"],
        cellLoc="center",
        loc="center",
        bbox=[0.05, 0.05, 0.90, 0.90],
    )
    summary_table.set_fontsize(11)
    summary_table.scale(1.2, 1.6)
    style_table(summary_table, "#2f5d8a", {0})

    scenario_ax.set_title(f"{STATE_NAME} Retirement Scenarios", fontsize=14, weight="bold", pad=8)
    scenario_table = scenario_ax.table(
        cellText=build_scenario_rows(scenarios),
        colLabels=[
            "Scenario",
            "401(k) / Monthly",
            "Roth IRA / Monthly",
            "Net Income / Monthly",
        ],
        cellLoc="center",
        loc="center",
        bbox=[0.03, 0.02, 0.94, 0.90],
    )
    scenario_table.set_fontsize(10)
    scenario_table.scale(1.0, 1.55)
    style_table(scenario_table, "#7a8ca5", {0})

    budget_ax.set_title(f"{STATE_NAME} Budget Splits", fontsize=14, weight="bold", pad=8)
    budget_table = budget_ax.table(
        cellText=build_budget_rows(scenarios),
        colLabels=[
            "Scenario",
            "Budget",
            "Needs / Monthly",
            "Wants / Monthly",
            "Savings / Monthly",
        ],
        cellLoc="center",
        loc="center",
        bbox=[0.02, 0.02, 0.96, 0.94],
    )
    budget_table.set_fontsize(9)
    budget_table.scale(1.0, 1.3)
    style_table(budget_table, "#5b7c99", {0, 1})

    fig.suptitle(
        f"{STATE_NAME} Tax Breakdown and Budget Planning for Gross Income of {format_currency(gross_income)}",
        fontsize=14,
        y=0.98,
    )
    plt.tight_layout()
    plt.show()


def main():
    federal = load_tax_brackets(FEDERAL_CSV)
    wisconsin = load_tax_brackets(WISCONSIN_CSV)

    gross_inc = int(input("How much are you making gross (no taxes) "))
    roth_annual_limit = float(
        input("Annual Roth IRA contribution to model (press Enter for 7500): ") or 7500
    )

    fed_tax = calc_tax(gross_inc, federal)
    state_tax = calc_tax(gross_inc, wisconsin)
    net_income = gross_inc - fed_tax - state_tax
    scenarios = build_scenario_data(gross_inc, federal, wisconsin, roth_annual_limit)

    show_tables(gross_inc, fed_tax, state_tax, net_income, scenarios)


if __name__ == "__main__":
    main()
