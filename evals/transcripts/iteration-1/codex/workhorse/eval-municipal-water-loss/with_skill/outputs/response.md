The strongest no-capex move is to stop treating “22% NRW” as a single pipe-leak target. First separate it into real loss, apparent loss, and unbilled authorized use; then reduce the loss-time and pressure excess that existing crews and controls can already influence. AWWA distinguishes real leakage from apparent losses caused by unmeasured or unbilled consumption. [AWWA water-loss guidance](https://www.awwa.org/resource/water-loss-control/)

“No new capital” can still mean staff time, routine maintenance materials, and reprioritized operating budget—not new meters, sensors, valves, or pipe replacement.

| Approach | Mechanism | Evidence that confirms it | Evidence that refutes it |
|---|---|---|---|
| Rebuild and data-grade the water balance monthly | Finds whether the 22% is physical loss, meter/billing error, or accounting timing; prevents solving a phantom problem | Three consecutive reconciliations show a stable residual after aligning production, reservoir change, billing read dates, authorized unbilled use, and known meter accuracy | The residual shifts materially when data inputs are corrected, or confidence bounds are too wide to tell whether 22% is real |
| Run a billing/revenue-protection exception sprint | Correct inactive accounts still consuming, wrong meter-account links, estimated-read backlogs, billing multipliers, and unauthorized use | Field checks of a random sample find a material, repeatable rate of incorrect/unbilled consumption; corrected accounts produce sustained billed-volume recovery | Sample checks show billing and account status are accurate, or recovered volume disappears after one billing cycle |
| Reprioritize repairs by estimated water lost per hour, not break count | A small continuous leak left open for weeks can outweigh many visible breaks; reduce awareness-to-repair time using existing crews and routine repair stock | Work orders show falling median/90th-percentile awareness-to-repair time, and completed repairs produce measured pre/post flow reductions | Faster repairs do not reduce normalized minimum-night flow or repair verification indicates low-flow leaks |
| Targeted active-leak “blitzes” using existing staff, maps, complaint history, valves, and acoustic equipment already owned | Focuses field effort on zones with high night flow, repeat breaks, pressure complaints, or unexplained supply-vs-billing gaps | The first set of targeted inspections locates more verified leakage per crew-hour than normal reactive work | Yield per crew-hour is no better than routine patrols, or pre/post zone flow does not move |
| Retune existing pressure-reducing valves, pump setpoints, and reservoir operating bands | Lowering excessive pressure reduces leak flow and stress; avoiding overflow and unnecessary high tank levels removes direct loss | A controlled trial in one existing pressure zone reduces normalized night flow while critical-point pressure, fire-flow requirements, complaints, and water-quality indicators remain acceptable | Pressure can’t be reduced without service/regulatory failure, or night flow is unchanged at a verified lower pressure. EPA notes that pressure-management level affects leakage rates. [EPA guidance](https://www.epa.gov/sites/default/files/2015-05/documents/epa816r10019.pdf) |
| Put overflow, flushing, and known operational discharges into an exception log | Makes recurring avoidable losses visible and assigns an operator owner; distinguishes required water-quality use from avoidable loss | Logged volume/time falls without adverse residual, turbidity, or compliance effects | Nearly all discharge is demonstrably required for water quality, fire protection, or operational safety |

The key reframing: the utility does not need to “find 22%.” It needs to identify which of three mechanisms dominates:

1. Water that never physically reaches a customer.
2. Water that reaches a customer but is not measured or billed.
3. Legitimate but unbilled/poorly recorded water.

Only the first is reduced by leak and pressure work. The second can improve revenue without saving a gallon, so report physical-water savings and revenue recovery separately.

Most contrarian hypothesis worth testing: a meaningful share of the reported 22% is accounting and measurement uncertainty rather than leakage. That is not a reason to dismiss NRW; it is a reason to avoid committing scarce crew capacity before the balance is credible. AWWA’s audit methodology specifically treats data validation as central to loss control. [AWWA](https://www.awwa.org/policy-statement/metering-and-accountability/)

Cheapest high-information experiment:

- Hypothesis: Existing pressure/operating controls and faster treatment of high-duration leaks can reduce real loss in one existing pressure zone without capital work.
- Critical assumption tested: The zone’s unexplained minimum-night flow is real leakage and is responsive to current controls.
- Experiment: For four weeks, choose one zone already bounded by existing meters/operational controls. Establish two weeks of baseline night flow and pressure; then make one reversible pressure/operating adjustment and enforce a same-day triage rule for high-loss repair tickets.
- Resources: Existing SCADA/billing/work-order data; one operations analyst; existing field crew; no new devices.
- Measured outcome: Normalized minimum-night flow, critical-point pressure, awareness-to-repair time, verified repair flow reduction, complaints, and water-quality exceptions.
- Success threshold: At least 10% lower normalized night flow versus baseline, with no service or compliance exception.
- Failure threshold: Less than 3% reduction, or any unacceptable pressure/water-quality impact.
- Learned either way: Whether pressure/repair-duration control is a material lever in this system.
- If validated: Extend the operating rule zone by zone and quantify annualized saved volume.
- If falsified: Stop scaling it; shift effort to balance validation and apparent-loss investigation.

Avoid spending effort on these as NRW solutions under the stated constraint:

- Customer leak alerts alone: customer-side leaks are normally billed water, not NRW.
- Blanket conservation campaigns: can reduce demand but do not establish where NRW occurs.
- New AMI, acoustic loggers, district meters, or PRV installations: potentially useful, but capital projects.
- Pipe replacement: not available now and poorly targeted until the loss profile is known.
- “More leak detection” without a repair-duration commitment: finding leaks faster does little if they remain open.

The missing facts that determine priority are annual treated volume, the audit’s data-grade/confidence, existing zone metering and controllable PRVs, current repair-cycle times, and whether routine repair labor/material budgets can be reprioritized.