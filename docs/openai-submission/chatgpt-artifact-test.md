# ChatGPT artifact test

**Status: NOT RUN.** No result in this file is filled in, and the compatibility
table records this host as UNTESTED until it is. The procedure exists so that the
run, when it happens, produces a record rather than an impression.

What is being tested is the **artifact**, not the repo. Installing from a clone
would test files that are not the ones being submitted; the whole point is to
find out whether the zip that goes to OpenAI behaves.

## Procedure

### 1. Build from the commit, not from the tag and not from the tree

```
python3 build/package.py --ref a9ee346
sha256sum dist/innovate-or-die-openai-v2.1.0.zip   # record this
```

Expected: `a370409ff480e41b440a62ddd402e43834b4b52a8dadae419ad5598365ebb3ab`,
17,918 bytes. **A different hash means you are not testing the recorded
artifact — stop and find out why before going further.**

`--ref v2.1.0` will not work: the tag predates this package, and the version in
the filename is not the artifact's identity. The commit and the checksum are.
See the provenance block in [README.md](README.md), which is where these values
are recorded and where any future build must also be recorded.

### 2. Extract and re-validate

```
mkdir -p /tmp/iod-artifact-test && cd /tmp/iod-artifact-test
unzip <path>/innovate-or-die-openai-v2.1.0.zip
python3 <repo>/build/validate_openai.py /tmp/iod-artifact-test
```

The validator reads a directory and a zip identically, so this is a genuine
re-check of the extracted tree rather than a repeat of the same read.

### 3. Install into a clean, temporary marketplace

Clean means clean: a marketplace or plugin directory with nothing else in it, and
**no clone of this repo on the path**. A stale `.agents/skills/innovate-or-die/`
or an installed Claude Code plugin will resolve the skill from disk, and the run
will look like a success that had nothing to do with the artifact. Remove the
temporary marketplace afterwards.

Confirm before running anything: the skill was discovered from the extracted
artifact, and from no other location.

### 4. Run the eight cases

Five from [positive-cases.md](positive-cases.md), three from
[negative-cases.md](negative-cases.md), **each in a fresh conversation** — a
second prompt in a session where the skill already ran tells you nothing about
whether it activates.

For each, record:

- **Activation** — is `⟦innovate-or-die v2.1.0⟧` on the first line? For the
  negative cases, absence is the pass.
- **Output shape** — kill list present? experiment with a pass/fail number
  present? mechanism attached to each opportunity? thesis first?
- **File resolution** — did the run reach `roles/`, `references/lenses.md` and
  `references/experiment-spec.md`, or only `SKILL.md`? The tell is content that
  can only have come from those files: the named lenses, the seven fake-novelty
  tests, the experiment spec's fields. A run that never opened them is running a
  fragment of the protocol.
- **Role observability** — is there any visible evidence the stages ran
  separately, or is it one pass with headings? **Assume the latter unless the
  host shows otherwise** — headings named after the roles are not evidence of the
  roles having run apart, and mistaking one for the other is exactly the error
  the fidelity levels in the README exist to prevent.

## Results

Blank until run. Fill in from the run, not from memory.

| # | Case | Activated | Output shape | File resolution | Role observability | Notes |
|---|---|---|---|---|---|---|
| P1 | Route density | | | | | |
| P2 | Dental no-shows (control) | | | | | |
| P3 | Municipal water loss | | | | | |
| P4 | Bookstore events | | | | | |
| P5 | SaaS onboarding churn | | | | | |
| N1 | Vendor comparison | | | | | |
| N2 | Implement approved design | | | | | |
| N3 | Summarize an article | | | | | |

| | |
|---|---|
| Date run | |
| Run by | |
| Commit SHA built from | |
| Artifact `sha256` | |
| Host and build | |
| Model | |
| Fidelity level observed | |
| Verdict | |

## What a failure means

- **A positive case does not activate.** Expected some of the time — activation is
  known to be non-deterministic and is documented as such in the README and the
  release notes. Record the count; do not retry until it works and record that.
- **A negative case activates.** More serious. It means the trigger description is
  too broad, and the fix is in `core/skill-meta.json` — a protocol change, an ADR,
  and a version bump, not an edit to a generated file.
- **File resolution fails.** The package layout is wrong for this host, or the
  host does not resolve bundled skill files at all. Either way the fidelity claim
  for ChatGPT drops and `docs/COMPATIBILITY.md` has to say so.
