-- Insert Inventory
INSERT INTO Inventory (sku, name, total_on_hand, allocated_stock, reserved_safety_stock, bin_location) VALUES
('SKU-1001', 'Widget A', 150, 20, 15, 'Zone A-01'),
('SKU-1002', 'Widget B', 50, 50, 10, 'Zone B-12'),
('SKU-1003', 'Lithium Battery Pack', 200, 10, 50, 'Zone A-04'),
('SKU-1004', 'Discontinued Item X', 0, 0, 0, 'Zone D-99'),
('WIDGET-X', 'Widget X', 5, 0, 5, 'Zone A-05');

-- Insert Orders
INSERT INTO Orders (order_id, customer_id, status, carrier, shipping_address) VALUES
('ORD-5001', 'CUST-881', 'PENDING', 'FedEx', '123 Main St, Springfield, IL'),
('ORD-5002', 'CUST-882', 'ALLOCATED', 'UPS', '456 Elm St, Austin, TX'),
('ORD-5003', 'CUST-883', 'PICKED', 'UPS', '789 Oak Ave, Seattle, WA'),
('ORD-5004', 'CUST-884', 'SHIPPED', 'FedEx', '321 Maple Dr, Denver, CO'),
('ORD-1042', 'CUST-999', 'ON_HOLD', 'FedEx', '123 Edge Case Ln, Chicago, IL');

-- Insert Order Items
INSERT INTO Order_Items (order_id, sku, quantity, allocated_quantity) VALUES
('ORD-5001', 'SKU-1001', 5, 0),
('ORD-5001', 'SKU-1003', 2, 0),
('ORD-5002', 'SKU-1002', 2, 2),
('ORD-5003', 'SKU-1003', 1, 1),
('ORD-5004', 'SKU-1001', 10, 10),
('ORD-1042', 'WIDGET-X', 2, 0);

-- Insert Shipments
INSERT INTO Shipments (tracking_number, order_id, carrier, current_status, last_scan_location, last_scan_timestamp, exception_code) VALUES
('TRK-FEDEX-9901', 'ORD-5004', 'FedEx', 'IN_TRANSIT', 'Denver, CO Hub', '2026-10-12 14:30:00', NULL),
('TRK-UPS-8802', 'ORD-5003', 'UPS', 'LABEL_CREATED', 'Fulfillment Center Dock', '2026-10-13 10:15:00', NULL),
('TRK-9821', 'ORD-5002', 'FedEx', 'EXCEPTION', 'Memphis, TN Hub', '2026-10-11 14:00:00', 'WEATHER_DELAY');