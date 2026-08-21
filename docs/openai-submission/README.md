# OpenAI Plugins Directory — submission materials

Everything the directory submission needs that is not code, plus the record of
what was actually submitted. **Status: submission pending.** Nothing here has
been through the portal yet, and no field below should be read as a result.

Scope: a **skills-only** package. No MCP server, no app, no network calls, no
credentials, no dependencies. The larger rule set that MCP-backed plugins face —
screenshots, four required listing URLs, domain verification, a mandatory five
positive and three negative test cases — does not apply, and
`build/validate_openai.py` deliberately does not implement it. The five positive
and three negative cases in this directory are ours: we wrote them because a
submission you cannot demonstrate is a submission you cannot defend, not because
the portal demanded them.

## What is here

| File | What it is for |
|---|---|
| [positive-cases.md](positive-cases.md) | Five prompts that should activate the skill, with the expected behaviour and result shape for each |
| [negative-cases.md](negative-cases.md) | Three prompts that should **not** activate it, with why |
| [release-notes.md](release-notes.md) | The submission's release notes, as filed |
| [attestation-checklist.md](attestation-checklist.md) | Every claim made to OpenAI, and where each one is verifiable |
| [chatgpt-artifact-test.md](chatgpt-artifact-test.md) | The procedure for testing the built artifact in ChatGPT, and the blank results table it fills in |

The listing copy itself is **not** here. It lives in
[core/listing-openai.json](../../core/listing-openai.json) and is generated into
`.codex-plugin/plugin.json` by `build/assemble.py`, because copy that exists in
two places drifts in one of them. That file's `_note` carries the publisher
decision verbatim.

## Building the artifact

```
python3 build/assemble.py --check     # generated trees match core/
python3 -m pytest -q                  # harness tests
python3 build/package.py --ref vX.Y.Z # builds all three assets into dist/
python3 build/validate_openai.py dist/innovate-or-die-openai-vX.Y.Z.zip
```

`package.py` runs the layout assertion and the validator on the finished zip
itself, so the last line is a re-check rather than the only check. Build from a
tag, never from the working tree: an asset built from uncommitted edits cannot be
reproduced by anyone, including you, and the mismatch surfaces only after it is
published.

The rule table behind the validator, with the source URL and read-date on every
entry:

```
python3 build/validate_openai.py --rules
```

## Recording what was submitted

Fill these in **after** the real build, from the artifact that is actually
uploaded. Blank means not yet done — it does not mean not applicable.

| | |
|---|---|
| Tag submitted | |
| Commit SHA (`git rev-parse vX.Y.Z^{commit}`) | |
| Artifact filename | |
| `sha256sum` of the artifact | |
| Date submitted | |
| Portal outcome | |

The SHA and the checksum are the whole point of this table. Builds are
reproducible — `python3 build/package.py --ref vX.Y.Z` from that SHA reproduces
the bytes — so recording both makes "is the thing in the directory the thing we
built?" a question with an answer.
