# Damaged Goods & Quarantine Protocol

## 1. Inspection Steps (Returns & Dock Damage)
All inbound items flagged as damaged (either from customer returns or inbound freight damage) must undergo a structured inspection.

1.  **Isolate:** Move the item(s) to the designated Quarantine Zone (Zone Q).
2.  **Photograph:** Take clear photos of the damage (minimum 3 angles: front, damaged area, barcode/serial number).
3.  **Evaluate:** Determine the extent of the damage using the Grading Scale (Section 3).
4.  **System Update:** Update the WMS with the appropriate condition code and status flag.

## 2. Quarantine Status Flags
Items in Zone Q must have one of the following flags applied in WMS:
*   `Q-WAIT-VENDOR`: Awaiting RMA or credit authorization from the vendor.
*   `Q-QA-INSPECT`: Awaiting QA team inspection for salvage grading.
*   `Q-HAZ-SPILL`: Hazardous material leak/spill. Requires immediate EHS (Environmental Health & Safety) intervention.

## 3. Disposal vs. Salvage Grading
QA must grade items to determine their final disposition:

| Grade | Condition | Action |
| :--- | :--- | :--- |
| **A** | Cosmetic box damage only. Product intact. | Repackage. Return to standard inventory (Zone A/B/C). |
| **B** | Minor product blemish. Fully functional. | Move to "Scratch & Dent" or Outlet inventory. |
| **C** | Product damaged. Not functional. | Salvage/Liquidation. Consolidate for bulk auction. |
| **F** | Destroyed, contaminated, or expired. | Certificate of Destruction (CoD) required. Dispose of per environmental guidelines. |

**Edge Case:** If an item is Grade F but contains PII (Personally Identifiable Information) or sensitive proprietary tech, it must be physically shredded before standard disposal.
