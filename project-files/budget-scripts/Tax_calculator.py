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


# Build monthly budget rows from annual net income using common budget split rules.
def build_budget_rows(net_income):
    monthly_net_income = net_income / 12
    budget_splits = [
        ("50/20/30", 0.50, 0.20, 0.30),
        ("60/30/10", 0.60, 0.30, 0.10),
        ("60/20/20", 0.60, 0.20, 0.20),
    ]

    rows = []
    for label, needs_pct, wants_pct, savings_pct in budget_splits:
        rows.append(
            [
                label,
                f"${monthly_net_income * needs_pct:,.2f}",
                f"${monthly_net_income * wants_pct:,.2f}",
                f"${monthly_net_income * savings_pct:,.2f}",
            ]
        )
    return rows


# Load federal and state tax bracket tables from CSV files.
federal = load_tax_brackets("federal.csv")
california = load_tax_brackets("california.csv")
colorado = load_tax_brackets("colorado.csv")


# Ask for gross income and compute taxes and net income for each state.
gross_inc = int(input('How much are you making gross (no taxes)'))

fed_tax = calc_tax(gross_inc, federal)
cal_tax = calc_tax(gross_inc, california)
co_tax = calc_tax(gross_inc, colorado)
cal_net = gross_inc - fed_tax - cal_tax
co_net = gross_inc - fed_tax - co_tax
state_tax_diff = cal_tax - co_tax
net_income_diff = co_net - cal_net


# Build the top summary table that compares taxes and net income by state.
summary_rows = [
    ["Gross income", f"${gross_inc:,.2f}", f"${gross_inc:,.2f}"],
    ["Federal tax", f"${fed_tax:,.2f}", f"${fed_tax:,.2f}"],
    ["State tax", f"${cal_tax:,.2f}", f"${co_tax:,.2f}"],
    ["Net income", f"${cal_net:,.2f}", f"${co_net:,.2f}"],
]


# Create one figure with a tax summary table and two monthly budget tables.
fig, axes = plt.subplots(
    3,
    1,
    figsize=(10, 9),
    gridspec_kw={"height_ratios": [1.0, 1.3, 1.3]},
)
summary_ax = axes[0]
summary_ax.axis("off")

# Draw the tax summary table at the top of the window.
summary_table = summary_ax.table(
    cellText=summary_rows,
    colLabels=["Category", "California", "Colorado"],
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

state_tables = [
    ("California", cal_net, axes[1]),
    ("Colorado", co_net, axes[2]),
]

# Draw and style the monthly allowed budget table for each state.
for state_name, net_income, ax in state_tables:
    ax.axis("off")
    ax.set_title(state_name, fontsize=14, weight="bold", pad=8)

    table = ax.table(
        cellText=build_budget_rows(net_income),
        colLabels=["Budget", "Needs / Month", "Wants / Month", "Savings / Month"],
        cellLoc="center",
        loc="center",
        bbox=[0.05, 0.02, 0.90, 0.88],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.15, 1.9)

# Style each state's monthly budget table.
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("black")
        cell.set_linewidth(1.2)

        if row == 0:
            cell.set_facecolor("#a6a6a6")
            cell.set_text_props(weight="bold")
        elif col == 0:
            cell.set_text_props(weight="bold")
        else:
            cell.set_facecolor("#f7f7f7")

# Add an overall title for the comparison window.
fig.suptitle(
    (
        f"Tax Breakdown and Budget Split for Gross Income of ${gross_inc:,.0f}\n"
        f"State tax difference: ${state_tax_diff:,.2f} | "
        f"Net income difference: ${net_income_diff:,.2f}"
    ),
    fontsize=14,
    y=0.98,
)

# Show the finished figure window.
plt.tight_layout()
plt.show()
