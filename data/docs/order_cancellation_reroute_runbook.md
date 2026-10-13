# Order Cancellation & Reroute Runbook

## 1. Cancellation Cutoffs
Customer Service Representatives (CSRs) can cancel orders based on the current WMS status.

### 1.1 Permitted Cancellations
Orders **CAN** be canceled if the status is:
*   `PENDING`: Order received, inventory not yet locked.
*   `ALLOCATED`: Inventory locked, but pick task not yet generated.

*Action:* System will auto-release inventory back to ATP.

### 1.2 Prohibited Cancellations
Orders **CANNOT** be canceled if the status is:
*   `PICKED`: Items are in a tote/cart and removed from bin location.
*   `PACKED`: Items are in a shipping carton with a label.
*   `SHIPPED`: Handed over to the carrier.

*Action:* CSR must inform the customer that the order is too far along in the fulfillment process. The customer must initiate a return once the item is received.

## 2. Address Intercept Procedures
If a customer requests an address change after the order has progressed past `ALLOCATED`:

### Scenario A: Order is PICKED or PACKED (Pre-Shipment)
1.  CSR submits a `REROUTE-URGENT` ticket.
2.  Exception Team locates the package on the dock or in the pack station.
3.  Package is set aside, the original label is voided, and a new label is generated with the corrected address.

### Scenario B: Order is SHIPPED (In Carrier Network)
1.  CSR must submit an intercept request directly via the Carrier Portal (FedEx Delivery Manager / UPS My Choice).
2.  Note: Carrier intercept fees ($15-$20) apply and success is not guaranteed.
3.  If the intercept fails and the package is delivered to the wrong address, follow the standard Lost/Misdelivered claims process.

**Edge Case - High Value Orders:** For orders > $1000, if an address change is requested post-allocation, the order MUST be flagged for manual fraud review before the reroute is approved.
