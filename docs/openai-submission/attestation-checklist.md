# Attestation checklist

Every claim this submission makes to OpenAI, and where each one can be checked.
The column that matters is the last one: a claim whose evidence is "we believe
so" is a claim to either verify or withdraw before filing.

Work down it immediately before submitting. Tick nothing in advance.

## The package

| # | Claim | How to verify | ✓ |
|---|---|---|---|
| 1 | Built from a tagged commit, not a working tree | `python3 build/package.py --ref vX.Y.Z`; the script reads only the ref through `git archive` | |
| 2 | The build is reproducible from that tag | build twice; `sha256sum` matches. Asserted by `tests/test_package.py` | |
| 3 | Generated trees match `core/` | `python3 build/assemble.py --check` exits 0 | |
| 4 | Harness tests pass | `python3 -m pytest -q` | |
| 5 | The artifact passes every directory rule | `python3 build/validate_openai.py dist/innovate-or-die-openai-vX.Y.Z.zip` exits 0 | |
| 6 | Exactly one plugin root, no sibling files | `unzip -l` shows a single top-level directory. Asserted by `assert_openai_layout` | |
| 7 | The member set is exactly what was intended | `EXPECTED_OPENAI` in `build/package.py`, asserted against the finished zip | |
| 8 | SHA and `sha256` of the submitted artifact are recorded | the table in [README.md](README.md) is filled in | |

## Skills-only scope

| # | Claim | How to verify | ✓ |
|---|---|---|---|
| 9 | No MCP server | no `.mcp.json`, no `mcpServers` key — rule `skills-only-exclusions` | |
| 10 | No app, no custom UI, no screenshots | no `.app.json`, no `apps` key, no `interface.screenshots` — same rule | |
| 11 | No credentials requested, stored, or transmitted | grep the package: it is Markdown, one manifest, one SVG, a licence | |
| 12 | No dependencies | nothing to install; no lockfile, no package manifest of any runtime | |
| 13 | No external network calls | the skill instructs a model over bundled Markdown; there is no code to make a call | |
| 14 | No user data collected, no telemetry | same — nothing in the package can emit anything | |

## The listing

| # | Claim | How to verify | ✓ |
|---|---|---|---|
| 15 | Every listing field comes from `core/listing-openai.json` | `codex_plugin()` in `build/assemble.py` copies `interface` through wholesale | |
| 16 | Field lengths are within the **final submission** limits, not just the upload limits | rules `display-name-length`, `short-description-length`, `developer-name-length` use the tighter of the two, and say so | |
| 17 | The category is one of the published categories | rule `category-allowed` | |
| 18 | Logo and composer icon exist, are square, and are self-contained | rules `branding-assets` and `svg-geometry`; the SVG has no script, no external href, no embedded font or image | |
| 19 | No privacy policy or terms URL is claimed | those pages do not exist; the fields are absent rather than filled with a placeholder | |
| 20 | The listing makes no unsupported effectiveness claim | `longDescription` states what the workflow does, and carries no count and no result figure — see the `_note` in `core/listing-openai.json` | |

## Identity and attribution

| # | Claim | How to verify | ✓ |
|---|---|---|---|
| 21 | Publisher is PESTalytix LLC **for this directory only** | `author.name` and `interface.developerName` in `.codex-plugin/plugin.json`, and nowhere else in the repo | |
| 22 | Authorship and copyright remain Ken Pendergast | `LICENSE`, `core/skill-meta.json`, `.claude-plugin/plugin.json` — all untouched by this submission | |
| 23 | The disclosure is in the consumer-facing copy | `longDescription` ends: "Created by Ken Pendergast. Published on OpenAI by PESTalytix LLC." | |
| 24 | The verified identity confirmed in the portal matches `developerName` | check at the confirmation step; a mismatch is silently normalised by the portal, which is why rule `author-matches-developer-name` requires equality in the artifact | |
| 25 | The licence permits this distribution | MIT, and the copyright holder is the person filing | |

## Behaviour, as demonstrated

| # | Claim | How to verify | ✓ |
|---|---|---|---|
| 26 | The five positive cases activate and return the documented shape | run them; record in [chatgpt-artifact-test.md](chatgpt-artifact-test.md) | |
| 27 | The three negative cases do not activate | same | |
| 28 | Limitations are disclosed rather than omitted | [release-notes.md](release-notes.md) — non-deterministic activation, cost, no local knowledge, no outcome evidence | |
| 29 | No claim is made that the protocol improves decisions | the evaluations establish output *structure*; the README and the release notes both say so explicitly | |

## Before filing

| # | | ✓ |
|---|---|---|
| 30 | The artifact tested in ChatGPT is the artifact being submitted — same SHA, same checksum | |
| 31 | Every row above is ticked, or the claim it covers has been removed from the submission | |
