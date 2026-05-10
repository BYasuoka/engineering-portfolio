"""Calculate monthly commute mileage and gas cost."""

"""https://gasprices.aaa.com/?state=CA""" # California average gas price link to AAA

import sys

MPG = 20
TANK_GALLONS = 20
GAS_PRICE_PER_GALLON = 5.5
WORK_DAYS_PER_WEEK = 5
WEEKS_PER_MONTH = 52 / 12
WEEKS_PER_YEAR = 52


def format_assumptions() -> str:
    return (
        f"Assumptions: {MPG} MPG, {TANK_GALLONS}-gallon tank, "
        f"${GAS_PRICE_PER_GALLON:.2f}/gallon, {WORK_DAYS_PER_WEEK} work days/week, "
        f"{WEEKS_PER_YEAR} weeks/year averaged across 12 months."
    )


def calculate_monthly_commute(one_way_miles: float) -> dict[str, float]:
    round_trip_miles = one_way_miles * 2
    monthly_work_days = WORK_DAYS_PER_WEEK * WEEKS_PER_MONTH
    monthly_miles = round_trip_miles * monthly_work_days
    monthly_gallons = monthly_miles / MPG
    monthly_cost = monthly_gallons * GAS_PRICE_PER_GALLON
    monthly_tanks = monthly_gallons / TANK_GALLONS

    return {
        "one_way_miles": one_way_miles,
        "round_trip_miles": round_trip_miles,
        "monthly_work_days": monthly_work_days,
        "monthly_miles": monthly_miles,
        "monthly_gallons": monthly_gallons,
        "monthly_cost": monthly_cost,
        "monthly_tanks": monthly_tanks,
    }


def prompt_for_commute_miles() -> float:
    commute_text = input("Enter your one-way commute distance in miles: ").strip()

    try:
        commute_miles = float(commute_text)
    except ValueError as exc:
        raise ValueError("Please enter a valid number of miles.") from exc

    if commute_miles <= 0:
        raise ValueError("Commute miles must be greater than 0.")

    return commute_miles


def main() -> int:
    try:
        one_way_miles = prompt_for_commute_miles()
        commute = calculate_monthly_commute(one_way_miles)
    except (RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print()
    print(f"One-way distance: {commute['one_way_miles']:.1f} miles")
    print(f"Round-trip distance: {commute['round_trip_miles']:.1f} miles")
    print(f"Estimated work days per month: {commute['monthly_work_days']:.2f}")
    print(f"Monthly miles on car: {commute['monthly_miles']:.1f} miles")
    print(f"Monthly gas used: {commute['monthly_gallons']:.1f} gallons")
    print(f"Estimated tanks per month: {commute['monthly_tanks']:.2f}")
    print(f"Estimated monthly gas expense: ${commute['monthly_cost']:.2f}")
    print()
    print(format_assumptions())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
