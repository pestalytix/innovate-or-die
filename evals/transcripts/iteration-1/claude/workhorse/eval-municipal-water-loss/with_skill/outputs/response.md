Non-revenue water (NRW) has three components under the standard IWA/AWWA M36 water balance: **real losses** (leakage), **apparent losses** (metering inaccuracy, theft, data/billing errors), and **unbilled authorized consumption** (flushing, firefighting, municipal use). Capital-free interventions exist in each bucket — they substitute labor, process, and existing-asset optimization for new construction or equipment purchases. Below are the main levers, with the evidence that would tell you whether each is actually working.

## 1. Rigorous water audit (AWWA M36 methodology)
**Approach:** Before optimizing anything, validate the 22% figure with a top-down/bottom-up water balance — most utilities that haven't done a formal audit are working from an estimate with wide error bars. This is analyst time, not capital.
**Evidence to confirm/refute:** A completed AWWA Free Water Audit Software (or equivalent) output with a Data Validity Score ≥ 7/10. If the recalculated NRW% or its split between real/apparent losses shifts materially from the 22% estimate, it tells you which of the levers below actually matters most — chasing leaks when the real problem is unmetered municipal use wastes effort.

## 2. Pressure management using existing infrastructure
**Approach:** Retune existing PRVs, close/open existing valves to reshape zones, shift to time-modulated or flow-modulated pressure control within current control logic. Reduces both leakage rate (background/unreported leaks scale with pressure, often N1 ≈ 0.5–1.5) and new break frequency.
**Evidence:** Minimum night flow (MNF) in the affected zone(s) before/after, normalized for legitimate night use. A 10% pressure reduction typically yields measurable MNF decline within days to weeks. If MNF doesn't move, either the zone isn't leak-dominated or the valve retuning didn't actually change average zone pressure — check pressure logger data, not just valve setpoint.

## 3. Active leakage control — speed and quality of repair
**Approach:** This isn't leak *detection* capex, it's process: prioritized dispatch, reduced time from report-to-repair, permanent (not temporary) repairs, and crew retraining on repair quality (many "fixed" leaks recur at the same joint). Often the single biggest lever because awareness-to-repair time is usually the dominant driver of real losses, more than undetected background leakage.
**Evidence:** Trend in average repair time (report-to-fix) and repeat-leak rate at the same location within 12 months. If NRW volume tracks down with shortened repair time and stays flat when repair time is flat, that's confirmation; if NRW is unchanged despite faster repairs, losses are elsewhere (background leakage, apparent losses).

## 4. Redeploy existing leak detection assets/staff (acoustic surveys, existing loggers)
**Approach:** If the utility already owns acoustic loggers, correlators, or has SCADA/AMI flow data, redirect existing staff time to systematic district-by-district survey rather than reactive-only response. This is a staffing/scheduling reallocation, not new equipment.
**Evidence:** Number and volume of previously unreported leaks found per survey-hour, and whether MNF in surveyed zones drops after found leaks are repaired. If survey hours produce few finds, the fixed real-loss component may already be low and effort should shift toward apparent losses.

## 5. Meter testing and calibration (not replacement)
**Approach:** Field-test a statistical sample of existing large/commercial meters (these disproportionately drive apparent-loss revenue impact even though they're a small fraction of the meter population) for under-registration. Recalibrate or reposition meters that test out of tolerance; this is testing labor, not new meter capex.
**Evidence:** Registration accuracy distribution from the test sample, and change in billed consumption for corrected accounts pre/post. If a meaningful share of large meters test below ~95% accuracy and correcting them raises billed volume without a corresponding change in production, that confirms apparent losses were material there.

## 6. Billing/GIS/customer database reconciliation
**Approach:** Audit for inactive-but-unbilled accounts, incorrect meter multipliers/constants in the billing system, address mismatches between GIS service connections and billing records, and stale "zero consumption" accounts that are actually occupied. Pure data-quality work.
**Evidence:** Count and billed-volume value of corrected accounts found per audit pass. A rising billed-consumption trend with no change in production or customer base confirms the fix; if corrected accounts are trivial in number, apparent losses aren't concentrated here.

## 7. Theft / illegal connection / meter tampering investigation
**Approach:** Targeted field investigation using existing production-vs-billed discrepancies by zone (if any DMA or zone metering already exists) to flag anomalous consumption patterns for site visits.
**Evidence:** Illegal connections or tampering incidents found per zone investigated, and change in zone-level apparent loss estimate after enforcement. Zero or trivial findings after a reasonable sample refutes this as a major driver here.

## 8. Unbilled authorized consumption controls
**Approach:** Tighten estimation and logging of flushing, hydrant use (fire department coordination), and construction/municipal water use so it's accounted for rather than defaulted into "loss." Sometimes a meaningful share of "NRW" is legitimate use that's simply unmeasured/unbilled — fixing the estimate doesn't reduce real loss but corrects the reported number and clarifies where remaining capital, once available, should go.
**Evidence:** Reconciliation of flushing/hydrant logs against production data. If unbilled authorized consumption, once properly estimated, explains several percentage points of the 22%, that's a reporting fix, not a loss-reduction win — worth stating explicitly to the utility board so capital isn't later misallocated chasing a phantom leak volume.

## 9. District Metering Area (DMA) analysis, if zone infrastructure already exists
**Approach:** If valves and boundary meters already exist (even if not a full formal DMA program), use them to isolate zones and compare production to billed consumption zone-by-zone, focusing effort where the gap is largest.
**Evidence:** Zone-level loss estimates ranked by volume; confirmed if targeted zones show disproportionately high MNF or unaccounted volume relative to connection count, refuted if losses are roughly uniform (suggesting a systemic apparent-loss or data problem rather than a localized real-loss problem).

---

### Sequencing note
Do #1 first — it's the only step that tells you whether the 22% is mostly real loss, apparent loss, or unbilled consumption, and that determines whether #2–4 (real loss) or #5–7 (apparent loss) deserve the operational effort. Running leak surveys against what's actually a metering-accuracy problem (or vice versa) is the most common way non-capital NRW programs underperform.