Non-revenue water (NRW) breaks into three categories under the standard IWA/AWWA M36 water balance — **real losses** (physical leakage), **apparent losses** (meter error, theft, data/billing error), and **unbilled authorized consumption** (firefighting, flushing, etc.). Most of the highest-leverage NRW work is operational, not capital — capital (pipe replacement, new PRVs, AMI rollout) mainly pays off *after* you've already found and prioritized the losses. Here's what's available within an opex/labor/software budget, organized by category, with the evidence that would tell you whether each is working.

## 1. Fix the measurement before you fix the loss

**AWWA M36 free water audit + data validation.** Run (or re-run) a validated water audit using AWWA's free software, focused on data grading (the audit assigns confidence scores to each input). A large share of "loss" at utilities that haven't done this recently turns out to be meter under-registration, billing lag, or unmetered authorized use misclassified as loss — not actual leakage.
- *Confirms value:* Data validity score improves year over year; the loss estimate shifts materially (up or down) after correcting known data errors — that shift itself is the value delivered.
- *Refutes value:* Audit converges to essentially the same 22% with high confidence on all inputs — tells you the number is real and effort should shift to categories 2–4.

## 2. Apparent losses — usually the fastest payback, zero capital

**Meter accuracy testing program (contracted, not purchased).** Pull a statistical sample of aging and large commercial/master meters, test on a contracted test bench or via a third-party testing service, no meter replacement required yet — just quantify under-registration.
- *Confirms:* Sample shows systematic under-registration (common in meters >15 years old or oversized commercial meters); apparent-loss estimate in the water audit tightens or grows, giving a defensible capital case later.
- *Refutes:* Sample shows accuracy within tolerance — apparent losses aren't the driver, redirect effort to real losses.

**Billing/CIS-to-GIS reconciliation.** Cross-reference the customer billing database against the asset/GIS inventory and field connection counts: zero-consumption active accounts, stopped/frozen meters, estimated-bill accounts running long, addresses in GIS with no billing record.
- *Confirms:* Each corrected exception recovers a known, trackable volume/revenue — sum these against the NRW estimate.
- *Refutes:* Exception rate is low (<1–2% of accounts) — data isn't the leak.

**Unauthorized use / illegal connection field survey.** Target areas by anomaly (low billed consumption vs. high system input in that zone).
- *Confirms:* Found connections, tampered meters, and their estimated volumes accumulate toward closing the NRW gap.
- *Refutes:* Survey turns up few findings relative to labor cost — deprioritize.

## 3. Real losses — active leakage control using existing assets

**District Metered Area (DMA) minimum night flow analysis**, using meters/SCADA/valves already in place (temporarily isolating zones with existing valves and portable/rented flow loggers rather than installed permanent meters).
- *Confirms:* Minimum night flow in a zone is elevated relative to legitimate night use — reliably locates unreported ("silent") leaks before they surface.
- *Refutes:* Night flow is consistent with expected legitimate use across zones — real losses are dominated by reported/visible leaks rather than hidden ones, so effort should go to repair speed instead.

**Acoustic leak survey / correlator work** with existing crews and either owned or short-term rented equipment.
- *Confirms:* Leaks-found-per-km-surveyed exceeds the break-even threshold (cost of survey vs. value of water saved); post-repair DMA night flow drops.
- *Refutes:* Survey yield is low and night-flow doesn't move after repairs — losses may be from a few large bursts rather than many small leaks; shift to background-loss modeling instead of blanket survey.

**Pressure optimization using existing PRVs** — retuning set points, adding time/flow-modulated control logic to valves already installed, rather than installing new ones.
- *Confirms:* Reduced average zone pressure correlates with reduced burst frequency and reduced background leakage rate (leakage scales roughly with pressure to a power >1).
- *Refutes:* Burst rate and night flow don't respond to pressure changes — losses are structural (pipe condition), which is a capital problem, not an operational one, and should be flagged for the next capital cycle.

**Active leakage control — shrinking awareness-to-repair time.** Faster leak reporting triage, crew scheduling changes, prioritization rules (no new headcount required, just process).
- *Confirms:* Trend line of average run-time (awareness → location → repair) shortens; cumulative leak-volume-days drops.
- *Refutes:* Repair time is already near the practical floor — further gains require more crews (capex/opex headcount), not process.

**Valve exercising / operability program.** Testing and freeing up existing isolation valves reduces water wasted during repairs (fewer/no downstream flushing events when a valve fails to close).
- *Confirms:* Valve operability rate rises; volume of water lost per repair event (due to inability to isolate cleanly) falls.
- *Refutes:* Valves already operate reliably — this isn't where the loss is.

## 4. Unbilled authorized consumption

**Better tracking/estimation of firefighting, flushing, and construction water use** (logbooks, hydrant meters already owned, standard estimation factors).
- *Confirms:* Previously "lost" volume gets reclassified as legitimate unbilled use, tightening the real NRW number (doesn't reduce total loss, but stops overstating it and refocuses the remaining categories).
- *Refutes:* Volume is immaterial — not worth the tracking overhead.

## 5. People and process

**Leak-detection crew training/certification + performance incentives** tied to DMA night-flow reduction or leaks-found rate.
- *Confirms:* Leak-find rate per crew-day rises after training relative to a baseline period.
- *Refutes:* No change — points to equipment or prioritization gaps, not skill.

**Public leak-reporting campaign** (low-cost outreach/hotline/rebate for reporting visible leaks).
- *Confirms:* Reported-leak volume as a share of total found leaks rises; average time-to-discovery for visible leaks shortens.
- *Refutes:* Reporting rate doesn't move — public awareness isn't the bottleneck.

---

**Sequencing note:** the audit/data-validation step (§1) should come first regardless — it tells you how much of the 22% is real losses vs. apparent losses vs. classification error, which determines whether §2 (fast, cheap, high-confidence wins) or §3 (slower, requires DMA infrastructure you may or may not already have) deserves the bulk of the operational effort over the next three years. If DMAs don't already exist, that's the one place this list brushes against capital — flag it now so it's queued for year four.