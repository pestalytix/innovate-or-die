⟦innovate-or-die v2.1.0⟧

The strongest fix is to stop treating a hygiene appointment as a confirmed reservation simply because a reminder was delivered. Treat it as perishable capacity that must be either recommitted early or released early enough to refill.

A 48-hour SMS is usually a notification, not a commitment system. It arrives after patients have already discovered a conflict—or too late to arrange work, childcare, or transport. The goal is not merely fewer “no-shows”; it is lower **unfilled chair loss**: no-shows plus late cancellations, minus successfully backfilled openings.

The important reframing: this is a demand-allocation problem, not primarily a messaging problem. A six-operatory practice should run two linked systems: make it easy for someone to honestly move an appointment early, and make every released slot easy to refill.

Top opportunities:

1. **Replace “reminder” with early intent collection.**  
   Send a 7–10 day message with two equally easy choices: “Keep this time” or “Choose a better time.” Then send the normal 48-hour reminder only to those who kept it. Nonresponders get a short human call only when their history indicates risk.  
   Mechanism: patients with conflicts reveal them while the slot is still usable; a one-click rebook removes the social friction of canceling.  
   Why it matters: even a temporary rise in reported cancellations is good if the opening is released early and refilled.  
   Biggest failure mode: requiring a reply without a genuinely easy reschedule path just creates more ignored messages.

2. **Build a small “standby hygiene” pool.**  
   Invite reliable, due-or-overdue patients to opt in for same-day openings—ideally those who live or work nearby and can arrive within a stated window. When an opening appears, send a sequential offer: “Can you be in the chair by 2:15? Reply YES.” Stop once accepted. Give them a convenience benefit, such as first access to preferred future times—not a clinically awkward discount.  
   Mechanism: converts unpredictable cancellations into a liquid inventory pool.  
   Why non-obvious: it fixes the financial loss even when patient behavior does not change.  
   Biggest failure mode: broadcasting to too many people, creating confusion, or promising an appointment before staff can actually reserve it.

3. **Change the reservation rules for repeat uncertainty, not for everyone.**  
   Do not blanket-charge or punish patients. Instead, after repeated late cancellations/no-shows, offer a choice: a short-horizon appointment, a less scarce time, or a reservation that requires an explicit reconfirmation. Keep the rule behavior-based, consistently applied, and never based on demographic proxies.  
   Mechanism: scarce prime-time capacity is no longer repeatedly assigned to the most uncertain reservations.  
   Why it matters: it protects the schedule without making access worse for the whole patient base.  
   Biggest failure mode: a punitive tone or policies that staff apply inconsistently. Review state rules, payer contracts, and signed financial-policy language before imposing fees or deposits.

Most contrarian hypothesis: **allow the no-show rate to look worse briefly.** If more patients voluntarily release appointments a week ahead, “cancellations” may rise—but the economically relevant measure, unfilled hygiene time, should fall sharply. Do not optimize the wrong dashboard.

Run this inexpensive four-week test first:

```text
Hypothesis: A 7–10 day keep-or-rebook message will release enough appointments early to reduce unfilled hygiene slots from ~14% to ≤8%.

Critical assumption tested: Patients with conflicts will act early when rescheduling is easier than ignoring a reminder.

Experiment: For the next 100 hygiene appointments, send a personalized two-choice SMS 7–10 days ahead:
“Reply 1 to keep [day/time]. Reply 2 and we’ll text available alternatives.”
Give staff a same-day task to process every “2.” Build an opt-in list of 30–50 standby patients and offer released slots sequentially.

Resources: One scheduling lead; ~30–45 minutes/day for four weeks; existing SMS and scheduling software; no new vendor.

Measured outcome: For test appointments, track early moves (>72 hours), late cancellations, no-shows, openings backfilled, and final unfilled chair loss. Compare with the prior 100 comparable hygiene appointments.

Success threshold: ≥10 early releases, ≥60% of released slots backfilled, and ≤8 unfilled appointments per 100.

Failure threshold: Fewer than 5 early releases or ≥12 unfilled appointments per 100 despite the extra workflow.

Learned either way: Whether the limiting factor is patient commitment, rescheduling friction, or lack of fill demand.

If validated: Automate the two-stage workflow and use a small reliability-based rule set for repeat misses.

If falsified: Stop tuning messages; audit no-shows by booking lead time, day/time, patient history, and stated reason to find the binding cause.
```

What I would not make the centerpiece:

- **More reminder messages:** usually a feature extension, not a new mechanism.
- **Blanket late fees/deposits:** can work for a narrow repeat-offender segment, but may trade capacity loss for goodwill and access loss.
- **Blanket double-booking:** shifts uncertainty into patient waiting time and clinical stress.
- **Generic AI no-show scoring:** useful later, but it does not create early release or replacement demand.
- **A passive waitlist:** it is only useful if it can accept a specific opening fast enough.

Assumptions to validate: most hygiene visits are booked far in advance; the practice has enough active/due patients to form a standby pool; and its software or staff can reliably offer alternatives. If the last assumption is false, the first operational priority is not better copy—it is a frictionless rescheduling workflow.