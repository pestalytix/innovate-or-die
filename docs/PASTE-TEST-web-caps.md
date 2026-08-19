# Paste test — ChatGPT Custom GPT and Gemini Gem instruction caps

**Why this exists.** Two of the three web targets have instruction-field character
limits with **no first-party source**. `docs/COMPATIBILITY.md` records both as
NEEDS VERIFICATION. The build currently assumes 8,000 for each, and the generated
instructions file is **7,874 characters — 126 under that assumption.** If the real
cap is lower, the primary web install path is already broken and we don't know it.

Only Microsoft's 8,000 is confirmed first-party. This test settles the other two.

**Time:** about 10 minutes per surface. You need a ChatGPT paid plan (Custom GPTs)
and a Gemini account that can create Gems.

---

## What you are actually testing

Three things, in priority order:

1. **Does our real file fit?** The only question that blocks shipping.
2. **What is the true cap?** Needed to set the budget in `build/assemble.py`.
3. **How does the field fail?** Hard rejection is safe — you find out immediately.
   **Silent truncation is dangerous**: the GPT looks fine, saves fine, and quietly
   drops the back half of the protocol. That is the outcome worth the most care.

---

## Test A — does the real file fit (do this first)

Per surface:

1. Open the builder — ChatGPT: *Explore GPTs → Create → Configure → Instructions*.
   Gemini: *Gems → New Gem → Instructions*.
2. Paste the whole of the matching file:
   - ChatGPT → `adapters/web/chatgpt-gpt-instructions.md` (7,874 chars)
   - Gemini → `adapters/web/gemini-gem-instructions.md` (7,874 chars)
3. **Save.** Then **reload the page** and reopen the instructions field.
4. Select all in the field, copy it out, and measure what actually survived:

   ```bash
   pbpaste | python3 -c "import sys; t=sys.stdin.read(); print(len(t), 'chars')"
   ```

   Compare to 7874. **Equal → it fits. Smaller → silent truncation, and the amount
   lost tells you roughly where the cap is.**

Step 3 is the one people skip. A field can accept a paste in the browser and truncate
on save; only the reload-and-recount proves what the model will actually see.

Also check the tail survived — the last line of the file should be the closing line of
the experiment spec. If the end is missing, it truncated:

```bash
tail -c 200 adapters/web/chatgpt-gpt-instructions.md
```

---

## Test B — find the actual cap (only if A truncates, or if you want the number)

Generate probe files of known length. Each is filler with a **unique end marker**, so
you can tell instantly whether the end survived:

```bash
python3 - <<'PY'
from pathlib import Path
out = Path.home() / "iod-cap-probes"; out.mkdir(exist_ok=True)
for n in (2000, 4000, 6000, 8000, 12000, 16000, 24000, 32000):
    head = f"PROBE-{n}-START "
    tail = f" PROBE-{n}-END"
    body = "x" * (n - len(head) - len(tail))
    (out / f"probe-{n}.txt").write_text(head + body + tail)
    print(f"wrote probe-{n}.txt  ({n} chars)")
print(f"\nfiles in: {out}")
PY
```

Then, per surface, working from smallest upward:

1. Paste `probe-N.txt`, save, reload.
2. Look for `PROBE-N-END` at the end of the field.
   - **Present** → N fits. Try the next size up.
   - **Missing / paste refused / error shown** → N exceeds the cap.
3. Once you have the largest N that fits and the smallest that doesn't, bisect
   between them if you want a precise number. Nearest 500 is plenty.

Note whether the tool **counts characters or tokens** — if a 8,000-char probe of
plain `x` fits but our 7,874-char real file doesn't, the field is counting tokens,
not characters, and the budget needs converting.

---

## What to log

Fill this in per surface and send it back — I'll fold it into
`docs/COMPATIBILITY.md` and set the real budgets in `build/assemble.py`.

```
SURFACE:            ChatGPT Custom GPT   |   Gemini Gem
DATE TESTED:
ACCOUNT PLAN:                             (Plus / Pro / Business / Ultra / Free —
                                           limits differ by plan, so this matters)

--- Test A: the real file (7,874 chars) ---
PASTE ACCEPTED?                           (yes / no / accepted-then-truncated)
CHARS SURVIVING AFTER SAVE+RELOAD:        (from the pbpaste measurement)
END MARKER INTACT?                        (does the experiment spec's last line survive?)
ERROR OR WARNING SHOWN?                   (quote it verbatim if any)

--- Test B: cap discovery (if run) ---
LARGEST PROBE THAT FIT:                   chars
SMALLEST PROBE THAT FAILED:               chars
=> CAP IS BETWEEN:                        and            chars
FAILURE MODE:                             (hard reject / silent truncation /
                                           warning but saves / counter turns red)
COUNTS CHARS OR TOKENS?                   (see note in Test B)

--- Anything surprising ---
```

### Why each field matters

- **Account plan** — ChatGPT's separate custom-instructions limit differs by plan
  (5,000 paid / 1,500 free), so the Custom GPT field plausibly varies too. A cap
  measured on Pro doesn't license a claim about Free.
- **Chars surviving after save+reload** — the only trustworthy measurement.
- **Failure mode** — decides whether the build's cap check can stay a warning or must
  become a hard failure for that target, like the instructions-over-cap rule.
- **Chars vs tokens** — changes the unit of the entire budget, not just its value.

---

## What happens with the results

- Real caps replace the assumed 8,000 in `WEB_TARGETS` in `build/assemble.py`, and
  the `verified` flag flips to `True` so the warning stops saying NEEDS VERIFICATION.
- `docs/COMPATIBILITY.md` gets the number, the date, the plan tested, and the method.
- **If any real cap is below 7,874**, that target's instructions file no longer fits
  and we have a decision to make: move content into the knowledge file, trim
  `principles.md`/`workflow.md`, or drop that target to the fallback rung. Current
  headroom against the *assumed* cap is only 126 characters, so this is live.

## Not covered here

The knowledge-file retrieval test is separate — that one checks whether the model can
read complete role sections on request with quotas intact, and it belongs to the
Phase E pre-publication pass. See the Phase E line in `docs/HANDOFF-2026-08-19.md`.
