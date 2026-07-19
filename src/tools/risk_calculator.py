from datetime import datetime
from langchain_core.tools import tool

# Mock baseline date to match our database context
CURRENT_DATE = datetime(2026, 7, 18).date()

# Days the FACTORY needs internally from this stage to finish production.
# in this calculation, it only matters for the buyer's delivery deadline,
DAYS_REQUIRED_FROM_STAGE = {
    "Fabric Dyeing": 15,
    "Cutting": 10,
    "Outsourced Printing": 12,
    "Stitching": 5,
    "Packing": 2,
}


@tool
def calculate_timeline_risk(current_stage: str, target_ship_date_str: str, transport_mode: str) -> str:
    """
    Computes the raw timeline numbers for an order -- how many days remain
    until the target ship date, and how many days the current stage
    typically still needs internally to finish production.

    IMPORTANT: this tool does NOT decide whether the order is at risk. It
    only reports numbers. You must apply judgment yourself: combine these
    numbers with the order's notes to reach a conclusion. Two orders can
    have the exact same numbers here and still be in very different real
    situations - e.g. one blocker that was just resolved vs. one that's
    still ongoing. Don't treat a negative buffer alone as automatic proof
    of risk, and don't treat a positive buffer as automatic proof of safety
    if the notes suggest otherwise.

    Args:
        current_stage: Current production stage (e.g., 'Cutting', 'Stitching').
        target_ship_date_str: Target ship date, 'YYYY-MM-DD'.
        transport_mode: 'Sea' or 'Air' -- informational only. Not used in
            this calculation, since transit happens after the ship date,
            not before it.

    Returns:
        A string with the raw numbers only -- no risk label. You classify it.
    """
    if current_stage not in DAYS_REQUIRED_FROM_STAGE:
        return f"Error: Unknown stage '{current_stage}'. Cannot compute timeline."

    required_days = DAYS_REQUIRED_FROM_STAGE[current_stage]
    target_date = datetime.strptime(target_ship_date_str, "%Y-%m-%d").date()
    days_remaining = (target_date - CURRENT_DATE).days
    buffer = days_remaining - required_days  # negative = behind schedule

    return (
        f"Stage '{current_stage}' typically needs {required_days} more days to finish internally. "
        f"{days_remaining} days remain until target ship date. "
        f"Buffer: {buffer} days ({'BEHIND schedule' if buffer < 0 else 'ahead of schedule'}). "
        f"Transport mode on file: {transport_mode} (not used in this calculation — informational only)."
    )