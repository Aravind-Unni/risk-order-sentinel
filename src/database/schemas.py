CREATE_ORDERS_TABLE = """
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    buyer TEXT NOT NULL,
    item_type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    target_ship_date DATE NOT NULL,
    transport_mode TEXT NOT NULL
);
"""

CREATE_PRODUCTION_TRACKING_TABLE = """
CREATE TABLE IF NOT EXISTS production_tracking (
    order_id TEXT PRIMARY KEY,
    current_stage TEXT NOT NULL,
    last_updated_date DATE NOT NULL,
    notes TEXT,
    FOREIGN KEY (order_id) REFERENCES orders (order_id)
);
"""