# Standard Operating Procedure: Inventory Allocation

## 1. Overview
This SOP defines the rules and protocols for inventory allocation, backordering, cycle count dispute resolution, and bin location prioritization within the fulfillment center.

## 2. Stock Allocation Logic
When an order is received, inventory is allocated based on a FIFO (First-In, First-Out) methodology combined with location proximity scoring.

### 2.1 Allocation Rules
*   **Status: Pending:** Order received but inventory not yet locked.
*   **Status: Allocated:** Inventory is logically reserved and deducted from ATP (Available to Promise).
*   **Status: Backordered:** Demand exceeds on-hand quantity.

### 2.2 Backorder Thresholds
*   **Standard Items:** Backorder if stock < 1.
*   **High-Velocity Items (Class A):** Backorder if safety stock drops below 10% of weekly average demand.
*   **Discontinued Items:** Do not backorder; cancel order line and notify customer service.

## 3. Bin Location Priority
To optimize pick paths, the WMS (Warehouse Management System) prioritizes locations as follows:

| Priority | Zone | Description | Handling Type |
| :--- | :--- | :--- | :--- |
| 1 | **Zone A** | Primary Pick Face | Eaches / Inner Packs |
| 2 | **Zone B** | Secondary Pick Face | Cases |
| 3 | **Zone C** | Bulk Storage | Pallets (Requires forklift) |
| 4 | **Zone D** | Overstock / Reserve | Replenishment only (Do not pick directly for orders) |

**Edge Case:** If an order requires a full pallet, WMS will bypass Zone A and allocate directly from Zone C to minimize touches.

## 4. Cycle Count Dispute Rules
Discrepancies found during cycle counts must be resolved before the end of shift.

*   **Discrepancy < 5% or < $50:** WMS automatically adjusts inventory.
*   **Discrepancy > 5% or > $50:** Requires Inventory Control Manager approval.
*   **Zero Count on Allocated Item:** If a picker reports a bin is empty but WMS shows stock, the bin is immediately locked. The order drops to exception management for reallocation, and an emergency cycle count is triggered for that bin.
