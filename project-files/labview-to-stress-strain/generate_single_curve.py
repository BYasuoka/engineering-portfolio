import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "4130 Steel 20C#1.lvm"
PORTFOLIO_DIR = BASE_DIR.parents[1]
OUTPUT_IMAGE = PORTFOLIO_DIR / "assets" / "images" / "4130-steel-20c-1-stress-strain.png"

# Current script defaults used as specimen assumptions for this sample.
GAUGE_LENGTH_MM = 33.21
CROSS_SECTION_AREA_MM2 = 3.23


def read_lvm_data(path: Path) -> pd.DataFrame:
    lines = path.read_text(errors="ignore").splitlines()
    header_idx = None
    for idx, line in enumerate(lines):
        if line.startswith("X_Value\t"):
            header_idx = idx
            break
    if header_idx is None:
        raise ValueError("Could not find data header row in LVM file.")

    cleaned_lines = [line for line in lines[header_idx:] if line.strip()]
    rows = list(csv.reader(cleaned_lines, delimiter="\t"))
    columns = [value for value in rows[0] if value]
    normalized_rows = []
    for row in rows[1:]:
        cleaned_row = row[: len(columns)]
        if len(cleaned_row) < len(columns):
            cleaned_row.extend([""] * (len(columns) - len(cleaned_row)))
        normalized_rows.append(cleaned_row)
    df = pd.DataFrame(normalized_rows, columns=columns).apply(pd.to_numeric, errors="coerce")
    return df.dropna(subset=["Force-N (Mean)", "Global Displacement-mm (Mean)"])


def build_plot():
    df = read_lvm_data(DATA_FILE)
    df["Global Strain"] = df["Global Displacement-mm (Mean)"] / GAUGE_LENGTH_MM
    df["Extensometer Strain"] = df["Extensometer Displacement-mm (Mean)"] / GAUGE_LENGTH_MM
    df["Stress (MPa)"] = df["Force-N (Mean)"] / CROSS_SECTION_AREA_MM2

    plot_df = df[df["Stress (MPa)"] >= 0].copy()

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=180)
    ax.plot(
        plot_df["Global Strain"],
        plot_df["Stress (MPa)"],
        color="#1f6a52",
        linewidth=2.6,
        label="Global displacement strain",
    )
    ax.plot(
        plot_df["Extensometer Strain"],
        plot_df["Stress (MPa)"],
        color="#c28b2c",
        linewidth=1.8,
        alpha=0.85,
        label="Extensometer strain",
    )

    ax.set_title("4130 Steel 20C #1 Stress-Strain Curve", fontsize=16, fontweight="bold")
    ax.set_xlabel("Engineering Strain (mm/mm)")
    ax.set_ylabel("Engineering Stress (MPa)")
    ax.legend(frameon=False)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    note = (
        f"Assumptions from current script defaults: gauge length = {GAUGE_LENGTH_MM:.2f} mm, "
        f"area = {CROSS_SECTION_AREA_MM2:.2f} mm^2"
    )
    fig.text(0.5, 0.01, note, ha="center", fontsize=9, color="#5f594f")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    OUTPUT_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_IMAGE, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    build_plot()
