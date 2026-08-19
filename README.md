# Innovate or Die

Innovate or Die is a skills-only plugin for ChatGPT and Codex. It searches beyond conventional advice, attacks its own proposals, revises what survives, and turns the strongest hypotheses into tests.

## What it does

The skill runs a staged workflow:

1. Map the conventional answer neighborhood and inherited assumptions.
2. Generate non-obvious candidate solutions.
3. Run an independent adversarial critique.
4. Reopen missing search spaces and revise.
5. Apply an eight-dimension quality gate.
6. Deliver the strongest user-facing answer with mechanisms, risks, and falsifiable tests.

Internal drafts and scores stay out of the final response unless the user asks for them.

## Use it

Invoke the skill explicitly:

```text
Use $innovate-or-die to rethink how my LinkedIn profile and website work together.
```

It may also activate implicitly for requests to challenge assumptions, escape generic advice, rethink a strategy, or find category-changing opportunities.

## Install for repository use

Copy `skills/innovate-or-die/` into your repository at:

```text
.agents/skills/innovate-or-die/
```

Restart Codex if the skill does not appear immediately.

## Plugin distribution

This directory is a complete skills-only plugin package. It contains the required `.codex-plugin/plugin.json` manifest and can be tested through a local marketplace before submission to the universal plugin directory.

## Privacy and permissions

The plugin declares no MCP servers, apps, hooks, external authentication, or API-key dependency. It does not transmit telemetry. If the host uses browsing or connected tools to ground an answer, the host's existing permissions and confirmation rules apply.

## Limitations

- Role separation improves search discipline but does not prove correctness.
- Novelty is not treated as evidence.
- Current or high-stakes claims still require authoritative external evidence.
- Strong conventional options are allowed to defeat weak unconventional ones.

## License

MIT
