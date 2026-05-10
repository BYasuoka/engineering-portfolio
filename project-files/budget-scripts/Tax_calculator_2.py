import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Load a tax bracket CSV and convert the string "inf" to a usable numeric value.
def load_tax_brackets(filename):
    filename = '/Users/hoodieb/Documents/VSCODE/Budget_scripts/' + filename
    df = pd.read_csv(filename)
    df["max"] = df["max"].replace("inf", np.inf)
    return df


# Calculate the total tax owed for a given income using progressive tax brackets.
def calc_tax(income, df):
    tax = 0

    for _, row in df.iterrows():
        lower = row["min"]
        upper = row["max"]
        rate = row["rate"]

        if income > lower:
            taxable = min(income, upper) - lower
            tax += taxable * rate
        else:
            break

    return tax


def calc_net_income(gross_income, federal_df, state_df, pretax_deduction=0):
    taxable_income = max(gross_income - pretax_deduction, 0)
    fed_tax = calc_tax(taxable_income, federal_df)
    state_tax = calc_tax(taxable_income, state_df)
    return gross_income - pretax_deduction - fed_tax - state_tax


def build_scenario_data(gross_income, federal_df, state_df, roth_annual_limit):
    monthly_roth = roth_annual_limit / 12
    annual_401k = gross_income * 0.04

    net_401k_only = calc_net_income(gross_income, federal_df, state_df, annual_401k)
    net_roth_only = calc_net_income(gross_income, federal_df, state_df) - roth_annual_limit
    net_both = calc_net_income(gross_income, federal_df, state_df, annual_401k) - roth_annual_limit

    return [
        {
            "name": "No retirement contributions",
            "monthly_401k": 0,
            "monthly_roth": 0,
            "monthly_net": calc_net_income(gross_income, federal_df, state_df) / 12,
        },
        {
            "name": "4% 401(k) only",
            "monthly_401k": annual_401k / 12,
            "monthly_roth": 0,
            "monthly_net": net_401k_only / 12,
        },
        {
            "name": "Roth IRA only",
            "monthly_401k": 0,
            "monthly_roth": monthly_roth,
            "monthly_net": net_roth_only / 12,
        },
        {
            "name": "4% 401(k) + Roth IRA",
            "monthly_401k": annual_401k / 12,
            "monthly_roth": monthly_roth,
            "monthly_net": net_both / 12,
        },
    ]


def build_scenario_rows(scenarios):
    rows = []
    for scenario in scenarios:
        rows.append(
            [
                scenario["name"],
                f"${scenario['monthly_401k']:,.2f}",
                f"${scenario['monthly_roth']:,.2f}",
                f"${scenario['monthly_net']:,.2f}",
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
        for label, needs_pct, wants_pct, savings_pct in budget_splits:
            monthly_net = scenario["monthly_net"]
            rows.append(
                [
                    scenario["name"],
                    label,
                    f"${monthly_net * needs_pct:,.2f}",
                    f"${monthly_net * wants_pct:,.2f}",
                    f"${monthly_net * savings_pct:,.2f}",
                ]
            )
    return rows


# Load federal and state tax bracket tables from CSV files.
federal = load_tax_brackets("federal.csv")
california = load_tax_brackets("california.csv")
colorado = load_tax_brackets("colorado.csv")


# Ask for state, gross income, and retirement contributions to model.
state_choice = input("Are you working in California or Colorado? ").strip().lower()
state_map = {
    "california": ("California", california),
    "ca": ("California", california),
    "colorado": ("Colorado", colorado),
    "co": ("Colorado", colorado),
}

if state_choice not in state_map:
    raise ValueError("Please enter California, CA, Colorado, or CO.")

state_name, selected_state_df = state_map[state_choice]
gross_inc = int(input('How much are you making gross (no taxes)'))
roth_annual_limit = float(
    input("Annual Roth IRA contribution to model (press Enter for 7000): ") or 7000
)

fed_tax = calc_tax(gross_inc, federal)
state_tax = calc_tax(gross_inc, selected_state_df)
net_income = gross_inc - fed_tax - state_tax
scenario_data = build_scenario_data(gross_inc, federal, selected_state_df, roth_annual_limit)


# Build the top summary table for the selected state.
summary_rows = [
    ["State", state_name],
    ["Gross income", f"${gross_inc:,.2f}"],
    ["Federal tax", f"${fed_tax:,.2f}"],
    ["State tax", f"${state_tax:,.2f}"],
    ["Net income before retirement", f"${net_income:,.2f}"],
]


# Create one figure with the summary, retirement scenarios, and budget splits.
fig, axes = plt.subplots(
    3,
    1,
    figsize=(13, 12),
    gridspec_kw={"height_ratios": [1.0, 1.3, 2.2]},
)
summary_ax = axes[0]
summary_ax.axis("off")

# Draw the tax summary table at the top of the window.
summary_table = summary_ax.table(
    cellText=summary_rows,
    colLabels=["Category", "Amount"],
    cellLoc="center",
    loc="center",
    bbox=[0.05, 0.05, 0.90, 0.90],
)

summary_table.auto_set_font_size(False)
summary_table.set_fontsize(11)
summary_table.scale(1.2, 1.6)

# Style the top summary table.
for (row, col), cell in summary_table.get_celld().items():
    cell.set_edgecolor("black")
    cell.set_linewidth(1.2)

    if row == 0:
        cell.set_text_props(weight="bold", color="white")
        cell.set_facecolor("#2f5d8a")
    elif col == 0:
        cell.set_text_props(weight="bold")
        cell.set_facecolor("#e8eef5")
    else:
        cell.set_facecolor("#f7f7f7")

scenario_ax = axes[1]
scenario_ax.axis("off")
scenario_ax.set_title(f"{state_name} Retirement Scenarios", fontsize=14, weight="bold", pad=8)

scenario_table = scenario_ax.table(
    cellText=build_scenario_rows(scenario_data),
    colLabels=[
        "Scenario",
        "401(k) / Month",
        "Roth IRA / Month",
        "Net Income / Month",
    ],
    cellLoc="center",
    loc="center",
    bbox=[0.05, 0.02, 0.90, 0.88],
)

scenario_table.auto_set_font_size(False)
scenario_table.set_fontsize(11)
scenario_table.scale(1.1, 1.7)

for (row, col), cell in scenario_table.get_celld().items():
    cell.set_edgecolor("black")
    cell.set_linewidth(1.2)

    if row == 0:
        cell.set_facecolor("#a6a6a6")
        cell.set_text_props(weight="bold")
    elif col == 0:
        cell.set_text_props(weight="bold")
    else:
        cell.set_facecolor("#f7f7f7")

budget_ax = axes[2]
budget_ax.axis("off")
budget_ax.set_title("Monthly Budget Splits by Scenario", fontsize=14, weight="bold", pad=8)

budget_table = budget_ax.table(
    cellText=build_budget_rows(scenario_data),
    colLabels=["Scenario", "Budget", "Needs / Month", "Wants / Month", "Savings / Month"],
    cellLoc="center",
    loc="center",
    bbox=[0.02, 0.01, 0.96, 0.93],
)

budget_table.auto_set_font_size(False)
budget_table.set_fontsize(10)
budget_table.scale(1.0, 1.45)

for (row, col), cell in budget_table.get_celld().items():
    cell.set_edgecolor("black")
    cell.set_linewidth(1.0)

    if row == 0:
        cell.set_facecolor("#6d8aa8")
        cell.set_text_props(weight="bold", color="white")
    elif col in (0, 1):
        cell.set_text_props(weight="bold")
        cell.set_facecolor("#eef3f8")
    else:
        cell.set_facecolor("#f7f7f7")

# Add an overall title for the comparison window.
fig.suptitle(
    (
        f"{state_name} Tax Breakdown, Retirement Scenarios, and Budget Splits\n"
        f"Gross Income: ${gross_inc:,.0f}\n"
        f"Roth IRA annual contribution modeled: ${roth_annual_limit:,.2f}\n"
    ),
    fontsize=14,
    y=0.98,
)

# Show the finished figure window.
plt.tight_layout()
plt.show()
