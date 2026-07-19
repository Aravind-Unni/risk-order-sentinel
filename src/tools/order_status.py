import os
import sqlite3
from datetime import datetime
from langchain_core.tools import tool

# Path targeting src/database/kavya_textiles.db relative to this file
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/kavya_textiles.db"))

CURRENT_DATE = datetime(2026, 7, 18).date()

STALE_THRESHOLD_DAYS = 3


@tool
def fetch_order_status(order_id: str) -> str:
    """
    Fetches the current production stage, last updated date, target ship
    date, transport mode, and supervisor notes for a given order_id.
    Use this tool FIRST when analyzing an order.

    The notes field often contains information the dates alone can't tell
    you -- e.g. whether a blocker is ongoing or was just resolved. Read it
    carefully; it can change your conclusion even when the numbers look
    the same as another order's.

    Args:
        order_id: The ID of the order (e.g., 'KT-104')

    Returns:
        A string with the order's full status, including how many days
        old the tracking data is -- or an error/not-found message.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = """
        SELECT p.current_stage, p.last_updated_date, p.notes,
               o.target_ship_date, o.transport_mode
        FROM production_tracking p
        JOIN orders o ON p.order_id = o.order_id
        WHERE p.order_id = ?
        """
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()

        if not result:
            return f"Order {order_id} not found in the database."

        stage, last_updated, notes, ship_date, transport = result

        last_updated_date = datetime.strptime(last_updated, "%Y-%m-%d").date()
        days_since_update = (CURRENT_DATE - last_updated_date).days
        staleness_flag = (
            f"⚠️ DATA IS {days_since_update} DAYS OLD -- exceeds the {STALE_THRESHOLD_DAYS}-day "
            f"freshness threshold. Treat this as unreliable; consider escalating as "
            f"INSUFFICIENT_DATA rather than judging risk from it."
            if days_since_update > STALE_THRESHOLD_DAYS
            else f"Data is {days_since_update} day(s) old -- within freshness threshold."
        )

        return (
            f"Order {order_id}: Stage is '{stage}'. "
            f"Last Updated on {last_updated} ({staleness_flag}) "
            f"Target Ship Date is {ship_date}. "
            f"Transport Mode: {transport}. "
            f"Supervisor notes: \"{notes if notes else 'No notes recorded.'}\""
        )

    except Exception as e:
        return f"Database error: {str(e)}"
    finally:
        if conn:
            conn.close()