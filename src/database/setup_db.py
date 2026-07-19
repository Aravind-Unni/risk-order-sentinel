import sqlite3
import os
from datetime import datetime, timedelta
from schemas import CREATE_ORDERS_TABLE, CREATE_PRODUCTION_TRACKING_TABLE

def init_db():
    db_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(db_dir, "kavya_textiles.db")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS production_tracking;")
    cursor.execute("DROP TABLE IF EXISTS orders;")

    cursor.execute(CREATE_ORDERS_TABLE)
    cursor.execute(CREATE_PRODUCTION_TRACKING_TABLE)

    # Baseline "today" for reproducible demo runs.
    today = datetime(2026, 7, 18).date()

   

    orders_data = [
        # --- 15 Normal On-Track Orders (realistic buffers, not huge slack) ---
        ("KT-101", "Zara UK", "Cotton T-Shirts", 5000, today + timedelta(days=8), "Sea"),
        ("KT-102", "Next Retail", "Polo Shirts", 3000, today + timedelta(days=10), "Sea"),
        ("KT-103", "H&M London", "Kids Hoodies", 8000, today + timedelta(days=16), "Sea"),
        ("KT-104", "Primark", "Denim Shorts", 12000, today + timedelta(days=12), "Sea"),
        ("KT-105", "ASOS", "Summer Dresses", 4000, today + timedelta(days=7), "Sea"),
        ("KT-106", "Marks & Spencer", "Linen Shirts", 2500, today + timedelta(days=11), "Sea"),
        ("KT-107", "Zara UK", "Baby Bodysuits", 15000, today + timedelta(days=18), "Sea"),
        ("KT-108", "Tesco Clothing", "Joggers", 9000, today + timedelta(days=21), "Sea"),
        ("KT-109", "Next Retail", "Knit Sweaters", 3500, today + timedelta(days=23), "Sea"),
        ("KT-110", "Sainsbury's", "Socks Pack", 20000, today + timedelta(days=6), "Sea"),
        ("KT-111", "H&M London", "Blouses", 4500, today + timedelta(days=9), "Sea"),
        ("KT-112", "Primark", "Pyjama Sets", 11000, today + timedelta(days=15), "Sea"),
        ("KT-113", "ASOS", "Crop Tops", 6000, today + timedelta(days=8), "Sea"),
        ("KT-114", "Zara UK", "Chinos", 3800, today + timedelta(days=13), "Sea"),
        ("KT-115", "Next Retail", "Cardigans", 2700, today + timedelta(days=14), "Sea"),

        # --- 3 Genuinely At-Risk Orders (required days > days remaining) ---
        ("KT-201", "Zara UK", "Premium Hoodies", 6000, today + timedelta(days=11), "Sea"),
        ("KT-202", "Next Retail", "Graphic Tees", 10000, today + timedelta(days=10), "Sea"),
        ("KT-203", "Primark", "Basic V-Necks", 18000, today + timedelta(days=7), "Sea"),

        # --- 1 Ambiguous Case: math says comfortably Viable, notes say otherwise ---
        ("KT-301", "H&M London", "Activewear Tops", 4000, today + timedelta(days=6), "Air"),

        # --- 1 Critical Failure Case: stale data AND math already at-risk ---
        ("KT-401", "ASOS", "Oversized Jackets", 3000, today + timedelta(days=10), "Sea"),
    ]

    tracking_data = [
        # Normal orders — last_updated staggered (0-2 days old) instead of
        # all being "today", since a real whiteboard/Excel tracker wouldn't
        # update every single order on the same day.
        ("KT-101", "Packing", today, "On schedule. Ironing finished."),
        ("KT-102", "Stitching", today - timedelta(days=1), "Stitching 70% complete."),
        ("KT-103", "Cutting", today - timedelta(days=2), "Fabric received and checked."),
        ("KT-104", "Stitching", today - timedelta(days=1), "Moving to checking tomorrow."),
        ("KT-105", "Packing", today, "Cartons being loaded."),
        ("KT-106", "Stitching", today - timedelta(days=2), "Sleeve attachment underway."),
        ("KT-107", "Cutting", today - timedelta(days=1), "Pattern alignment completed."),
        ("KT-108", "Fabric Dyeing", today, "Yarn dyed successfully."),
        ("KT-109", "Fabric Dyeing", today - timedelta(days=1), "Batch 2 in progress."),
        ("KT-110", "Packing", today - timedelta(days=2), "Final inspection passed."),
        ("KT-111", "Stitching", today, "Main labels attached."),
        ("KT-112", "Cutting", today - timedelta(days=1), "Assorted sizing cut completed."),
        ("KT-113", "Packing", today - timedelta(days=2), "Polybag packaging ongoing."),
        ("KT-114", "Stitching", today, "Waistband stitching."),
        ("KT-115", "Cutting", today - timedelta(days=1), "Initial sampling approved, cutting started."),

        # --- At-risk orders: fresh data (not stale), math is genuinely tight ---

    
        ("KT-201", "Fabric Dyeing", today, "Delayed due to chemical shortage at dye house. Still no ETA from supplier."),

        # KT-202: math says at-risk (shortfall ~2 days), but notes say the
        # blocker was JUST resolved. This is your deliberate reasoning test --
        # see if the agent's alert tone/urgency changes vs. KT-201, or if it
        # treats both identically (which would mean it's only reading the math).
        ("KT-202", "Outsourced Printing", today, "Vendor confirmed machine repaired this morning -- printing resumed, expects to finish within 2 days."),

        # KT-203: math at-risk, notes confirm an ongoing structural problem
        # (staff shortage, not a one-off breakdown) -- should read as serious.
        ("KT-203", "Cutting", today, "Only 20% of fabric layout completed. Staff shortage continues, no replacement workers arranged."),

        # KT-301 (ambiguous): math says comfortably Viable (6 days left,
        # only 2 required from Packing) -- but notes reveal a real external
        # blocker the date-math can't see. Tests whether the agent looks
        # past a "Viable" verdict when the notes say otherwise.
        ("KT-301", "Packing", today, "Production finished, but held at customs clearance for final packaging boxes -- 2 days and counting, no confirmed release date."),

        # KT-401 (stale + at-risk): last updated 12 days ago AND math already
        # says at-risk on the last known stage. Two failure signals stacked --
        # this is your flag_insufficient_data / escalation demo case.
        ("KT-401", "Fabric Dyeing", today - timedelta(days=12), "Stuck at dye house lab test validation. No further update since."),
    ]

    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?);", orders_data)
    cursor.executemany("INSERT INTO production_tracking VALUES (?, ?, ?, ?);", tracking_data)

    conn.commit()
    conn.close()
    print(f"Database successfully generated at: {db_path}")

if __name__ == "__main__":
    init_db()