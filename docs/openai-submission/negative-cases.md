# Negative cases — the skill should not activate

Three prompts that sit close enough to the skill's territory to be a real test,
and on which it should stay out of the way. An ordinary, direct answer is the
correct outcome for all three.

**How to tell.** The activation marker `⟦innovate-or-die v2.1.0⟧` is the tell. If
it is on the first line, the skill ran and the case failed. The secondary tells
are the protocol's own artifacts: a kill list of rejected ideas, or an experiment
with a pass/fail threshold, appearing in an answer to a question that asked for
neither.

**Why these three and not three unrelated prompts.** A negative set made of
"what's the weather" proves nothing — no skill would fire on it. Each of these
shares surface features with the skill's real triggers (a business decision, a
strategy document, an ambiguous "what should we do") while being one of the two
jobs the skill is explicitly the wrong tool for, or no job at all.

---

## 1 — Vendor comparison

> We've shortlisted Zendesk, Freshdesk, and Intercom for our support desk. 40
> agents, mostly email, some chat. Which one should we go with?

**Expected: does not activate. An ordinary comparison answer.**

**Why.** The options are already defined and the ask is to pick one. That is
decision analysis, not search — the skill's own instructions name it as out of
scope. The failure mode this case guards against is the skill firing on any
business question with the word "should" in it and answering a decision with
thirty candidate reframings nobody asked for.

## 2 — Implement an approved design

> Here's the migration plan we agreed on last week: move the jobs table to
> Postgres partitioning by month, backfill in batches of 50k, cut over behind a
> feature flag. Write the migration script.

**Expected: does not activate. It writes the script.**

**Why.** The plan exists and was agreed. This is execution, the second job the
skill is explicitly wrong for. It is also the most damaging false positive in the
set: a skill that responds to an approved plan by attacking its assumptions has
reopened a decision someone already closed, and costs the user their time to say
"no, just write it."

## 3 — Summarize an article

> Can you summarize this article on remote work productivity research?

**Expected: does not activate. A summary.**

**Why.** No problem is being solved; the user wants compression of something they
already have. This case catches activation on topic-matching alone — "productivity",
"research", and a knowledge-work subject are all in the skill's neighbourhood
without any of them being a request for non-obvious options.
