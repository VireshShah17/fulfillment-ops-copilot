CREATE TABLE Inventory (
    sku VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    total_on_hand INT NOT NULL DEFAULT 0,
    allocated_stock INT NOT NULL DEFAULT 0,
    reserved_safety_stock INT NOT NULL DEFAULT 0,
    bin_location VARCHAR(50)
);

CREATE TABLE Orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('PENDING', 'ALLOCATED', 'PICKED', 'PACKED', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'ON_HOLD')),
    carrier VARCHAR(50),
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Order_Items (
    order_id VARCHAR(50),
    sku VARCHAR(50),
    quantity INT NOT NULL,
    allocated_quantity INT NOT NULL DEFAULT 0,
    PRIMARY KEY (order_id, sku),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (sku) REFERENCES Inventory(sku)
);

CREATE TABLE Shipments (
    tracking_number VARCHAR(100) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    carrier VARCHAR(50),
    current_status VARCHAR(50),
    last_scan_location VARCHAR(255),
    last_scan_timestamp TIMESTAMP,
    exception_code VARCHAR(50),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);
