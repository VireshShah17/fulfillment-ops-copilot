import sqlite3
import contextlib
import os
import json
from mcp.server.fastmcp import FastMCP


# Initialize the FastMCP server
mcp = FastMCP("OpsDatabaseServer")
DB_PATH = os.path.abspath("data/db/ops.sqlite")


# Robust read-only database helper
@contextlib.contextmanager
def get_db_connection():
    """
        Opens a read-only connection to the SQLite database.
        Yields the connection object and ensures it closes securely.
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    db_uri = f"file:{DB_PATH}?mode=ro"
    # Establish a connection with URI parameters enabled
    conn = sqlite3.connect(db_uri, uri=True)
    # Return rows as dictionary-like objects
    conn.row_factory = sqlite3.Row

    try:
        yield conn
    finally:
        conn.close()


@mcp.tool()
def get_order_status(order_id: str) -> str:
    """
        Returns the status, carrier, and shipping address for a given order.
    """
    query = "SELECT status, carrier, shipping_address FROM orders WHERE order_id = ?"

    with get_db_connection() as conn:
        row = conn.execute(query, (order_id,)).fetchone()

        if not row:
            return f"Order not found for ID: {order_id}"
        
        return json.dumps(dict(row))


@mcp.tool()
def get_inventory_levels(sku: str) -> str:
    """
        Returns total on hand, allocated, and safety stock for a given SKU.
    """
    query = "SELECT total_on_hand, allocated_stock, reserved_safety_stock FROM inventory WHERE sku = ?"

    with get_db_connection() as conn:
        row = conn.execute(query, (sku,)).fetchone()

        if not row:
            return f"SKU not found in inventory: {sku}"
        
        return json.dumps(dict(row))


@mcp.tool()
def get_shipment_tracking(tracking_number: str) -> str:
    """
        Returns current status, location, and exception codes for a tracking number.
    """
    query = "SELECT current_status, last_scan_location, exception_code FROM shipments WHERE tracking_number = ?"
    with get_db_connection() as conn:
        row = conn.execute(query, (tracking_number,)).fetchone()

        if not row:
            return f"Tracking number not found: {tracking_number}"
        
        return json.dumps(dict(row))


if __name__ == '__main__':
    # Start the FastMCP server
    mcp.run()
