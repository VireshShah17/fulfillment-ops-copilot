import unittest
import json
import os
import sys


# Ensure the mcp_server package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_server.server import get_order_status, get_inventory_levels, get_shipment_tracking


class TestMCPTools(unittest.TestCase):


    def test_get_order_status_success(self):
        result = get_order_status("ORD-1042")
        self.assertNotIn("not found", result.lower())
        data = json.loads(result)
        self.assertIn("status", data)
        self.assertIn("carrier", data)
        self.assertEqual(data["status"], "ON_HOLD")


    def test_get_order_status_not_found(self):
        result = get_order_status("ORD-9999")
        self.assertEqual(result, "Order not found for ID: ORD-9999")


    def test_get_inventory_levels_success(self):
        result = get_inventory_levels("SKU-1004")
        
        if "not found" not in result.lower():
            data = json.loads(result)
            self.assertIn("total_on_hand", data)
            self.assertIn("reserved_safety_stock", data)


    def test_get_inventory_levels_not_found(self):
        result = get_inventory_levels("FAKE-SKU")
        self.assertEqual(result, "SKU not found in inventory: FAKE-SKU")

    def test_get_shipment_tracking_success(self):
        result = get_shipment_tracking("TRK-UPS-8802")
        
        if "not found" not in result.lower():
            data = json.loads(result)
            self.assertIn("current_status", data)
            self.assertIn("last_scan_location", data)


    def test_get_shipment_tracking_not_found(self):
        result = get_shipment_tracking("TRK-00000")
        self.assertEqual(result, "Tracking number not found: TRK-00000")


if __name__ == '__main__':
    unittest.main()
