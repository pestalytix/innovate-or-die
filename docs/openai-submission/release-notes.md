# Release notes — initial OpenAI directory submission

**Innovate or Die — skill v2.1.0. First submission to the OpenAI Plugins
Directory.** The skill protocol itself is unchanged by this submission; v2.1.0 is
the version already published on the other install surfaces.

## What this plugin is

A staged workflow for problems where the conventional answer is already known and
the value is in what was overlooked. It restates the problem and names the
obvious answer before generating anything, opens a wide field of candidate
approaches each carrying its mechanism, attacks that field for fake novelty and
for constraints that were inherited rather than checked, pushes the survivors
further, and scores the result against a quality gate before it is delivered.

The delivered answer leads with the strongest thesis and carries a reframing, the
opportunities worth pursuing with mechanisms, the most contrarian hypothesis, the
cheapest experiment that would falsify it, a kill list of what was rejected, and
what may still be missing.

## What is in the package

A **skills-only** plugin, under one top-level directory:

```
innovate-or-die/
  .codex-plugin/plugin.json          manifest and directory listing metadata
  skills/innovate-or-die/
    SKILL.md                         the protocol entry point
    principles.md
    roles/{innovator,critic,reviser,evaluator}.md
    references/{lenses,experiment-spec}.md
  assets/logo.svg                    the listing logo and composer icon
  LICENSE                            MIT
```

## What is not in it

- **No MCP server.** No `.mcp.json`, no `mcpServers` field.
- **No app.** No `.app.json`, no `apps` field, no custom UI, no screenshots.
- **No credentials of any kind.** Nothing is requested, stored, or transmitted.
- **No dependencies.** Nothing to install; the package is Markdown, one manifest,
  one SVG, and a licence.
- **No external calls.** The skill does not fetch, post, or reach any network
  service. It reads its own bundled Markdown files and nothing else.
- **No user data collection.** There is no telemetry and nothing to opt out of.
  This is also why no privacy policy or terms URL is listed: those pages do not
  exist, and a placeholder URL in a listing field is a claim we cannot support.

## Known limitations, stated up front

- **It does not always activate**, and it does not announce that it sat out. The
  activation marker on the first line of the answer is the only reliable tell.
  Naming the skill in the request is the reliable way to invoke it.
- **It is slow and it consumes more tokens than a direct answer**, because it
  generates and discards a great deal before answering. That is the trade the
  design makes.
- **It does not know your prices, local rules, or regulations.** Where an idea
  depends on a figure it was not given, it is instructed to name what you need to
  look up rather than invent one.
- **Whether the protocol yields better decisions is not established.** What our
  published evaluations show is that the output structure appears reliably with
  the skill and rarely without it. That is a claim about structure, not outcomes.

## Publisher

Created by Ken Pendergast. Published on OpenAI by PESTalytix LLC.

## Source

<https://github.com/pestalytix/innovate-or-die> — MIT licensed. The whole
package is generated from `core/` by `build/assemble.py`, built by
`build/package.py` from a git tag, and checked against the directory's rules by
`build/validate_openai.py`. Builds are byte-reproducible from the tag.
