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
python3 build/assemble.py --check      # generated trees match core/
python3 -m pytest -q                   # harness tests
python3 build/package.py --ref a9ee346 # builds all three assets into dist/
python3 build/validate_openai.py dist/innovate-or-die-openai-v2.1.0.zip
```

`package.py` runs the layout assertion and the validator on the finished zip
itself, so the last line is a re-check rather than the only check. Build from a
committed ref, never from the working tree: an asset built from uncommitted edits
cannot be reproduced by anyone, including you, and the mismatch surfaces only
after it is published.

**The ref is a commit, not the `v2.1.0` tag.** See the note under the provenance
block below — the tag predates this package and cannot build it.

The rule table behind the validator, with the source URL and read-date on every
entry:

```
python3 build/validate_openai.py --rules
```

## Provenance of the built artifact

The artifact exists and its identity is recorded. It has **not** been submitted;
the rows below the rule are still blank, and blank means not yet done rather than
not applicable.

| | |
|---|---|
| Source commit | `a9ee346cf544` |
| Artifact | `innovate-or-die-openai-v2.1.0.zip` (17,918 bytes) |
| SHA-256 | `a370409ff480e41b440a62ddd402e43834b4b52a8dadae419ad5598365ebb3ab` |
| Built with | `python3 build/package.py --ref a9ee346` |
| Verified | Ken rebuilt from `a9ee346` on 2026-08-21; the hash matched the two Claude Code builds byte-for-byte |
| | |
| Date submitted | |
| Portal outcome | |

**Build this package from `a9ee346`, not from the `v2.1.0` tag.** The skill tree
inside the zip is byte-identical to the skill at the v2.1.0 tag — the protocol
did not change — but the *package* did not exist at that tag: the manifest's
listing block, `assets/logo.svg` and the bundled `LICENSE` were all added
afterwards, so `--ref v2.1.0` cannot reproduce these bytes and will not produce a
submittable plugin at all. The version number in the filename comes from
`core/skill-meta.json`, which is deliberately unchanged, and is therefore *not*
the identity of this artifact. The commit and the checksum are.

That is what makes the two rows above worth writing down: the build is
reproducible from the commit, so "is the thing in the directory the thing we
built?" is a question with an answer rather than a matter of trust.
