# Jessica's synthetic complete-workflow demonstration

## Before the meeting

Start only the synthetic complete-workflow demonstration:

```bash
./run_synthetic_demo.sh
```

Open **Synthetic complete workflow demo**. Confirm that the amber notice says
**SYNTHETIC DEMONSTRATION DATA — NOT FOR OPERATIONAL USE**.

## Suggested 8–10 minute talk script

### 1. Purpose

“This demonstration shows how the control converts nine source packages into a
dated item-level inventory-and-commitment schedule. All figures and identifiers
in this cycle are made up and must not be used operationally.”

### 2. Input register

“The Input Register shows all nine packages received for Walmart week 202630.
Each package retains its original file, extraction time, report identifier,
filters, processing status and row count.”

Point out P01 through P09 and their **Populated** status.

### 3. Reconciliation logic

“For each item, usable supply combines available eCommerce inventory, available
factory finished goods and available RJW inventory. Confirmed inbound is counted
only when it is available in time for the commitment. Current unreceived PO
quantities are then deducted, followed by the approved buffer.”

Use this formula:

`Projected gap = usable supply + confirmed on-time inbound - current commitments - approved buffer`

Before opening the quantified schedule, select **Route control**.

“The route view separates physical positions from commitments. It also shows
three confirmed item configurations, one provisional identifier and one
unresolved controlled entry. The two mapping examples are deliberately excluded
from supply calculations: they demonstrate why identifier evidence must be
approved before records are matched automatically.”

Open **DEMO-PROVISIONAL** and **DEMO-UNRESOLVED** in the Mapping Review Queue.

Select **Geography**.

“The geographic view answers where a supported handoff is located. Every pin in
this demonstration is synthetic. Solid green lines represent recorded demo
links; dashed amber lines are provisional. Clicking a marker filters the same
supporting item grid, while unlocated stages remain listed beneath the map.”

### 4. Three illustrative outcomes

**DEMO-SURPLUS**

“Available supply is 900 units: 150 eCommerce, 250 factory and 500 RJW. Adding
300 on-time inbound and deducting 700 commitments and a 100-unit buffer produces
a 400-unit projected surplus. The suggested status is Monitor.”

**DEMO-SHORTAGE**

“Available supply is 250 units. After 100 units of on-time inbound, 600 units of
commitments and a 100-unit buffer, the projected gap is negative 350 units.
The item requires investigation before any supply action is authorized.”

**DEMO-LATE**

“Available supply is 400 units against 500 units of commitments and a 50-unit
buffer, producing a negative 150-unit gap. A further 600 units exist in the
pipeline, but their expected availability is after the current MABD, so the
control excludes them from on-time supply and raises a timing exception.”

### 5. Control gate

“Unlike the real partial-data trial, this synthetic cycle has all critical
packages and therefore produces quantified results. A negative gap or timing
exception does not automatically authorize a response; it identifies the item
that requires Jessica's documented recommendation and follow-up.”

### 6. Six decision-support analyses

Open **View calculation** for an item and scroll to **Six forward-decision
analyses**.

“The same nine packages now support six distinct reviews: total supply coverage,
the forward-plan variance against recent orders, PO-line OTIF recovery, backward
modular milestones, incremental traited-store loading, and FC-level eCommerce
coverage. Every card distinguishes calculated evidence from confirmation still
required.”

Point out that the synthetic example shows:

- last-four-week actual orders versus the next-week supply plan;
- on-time and in-full percentages with PO-line exception counts;
- factory release, ETD, ETA and expected warehouse availability;
- the expected system-order week and modular-set week;
- 210 incremental stores and an explicitly illustrative 630-unit initial fill;
- SKU-level eCommerce weeks of supply and FC count.

“These outputs are potential recommendations for review. They do not constitute
production, purchase, or shipment authorization.”

### 7. Record and export

Open an item, show the recommendation and decision-note fields, then return to
the cycle.

“The results can be exported as a spreadsheet or printed to PDF. Both outputs
retain the synthetic-data warning.”

The Excel export includes a **Decision Support** sheet containing the underlying
measures.

### 8. Closing

“The demonstration illustrates the intended end state: one dated schedule that
separates covered demand, shortages and late supply, while preserving the source
files and exception trail behind each conclusion.”
