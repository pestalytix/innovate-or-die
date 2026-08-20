#!/usr/bin/env python3
r"""Copy the publishable slice of `evals-workspace/` into `evals/transcripts/` and
redact it.

    python3 evals/runners/redact_transcripts.py --copy-from evals-workspace
    python3 evals/runners/redact_transcripts.py --dry-run
    python3 evals/runners/redact_transcripts.py            # redact in place

`evals-workspace/` is the local-only working tree and stays gitignored. This
script produces the committed, publishable copy: the raw evidence behind the
files in `evals/results/`, with local identifiers removed.

WHAT IS COPIED is an allowlist (`COPY_NAMES`), not a denylist. A denylist over a
working tree publishes whatever a future run happens to drop there; an allowlist
publishes only the five artifact kinds that were reviewed for this purpose.

IDEMPOTENT by construction: every replacement's output is a fixed point of the
rule that produced it (`/Users/REDACTED/` re-matches the generic user-path rule
and maps to itself; the `[REDACTED-*]` tokens match none of the secret patterns).
Re-running changes nothing and reports zero replacements.

READBACK ASSERTION: after writing, every file is re-read FROM DISK and rescanned
with the same patterns. Any surviving match exits 1. The write is never trusted
-- the same discipline `report.py` applies to its completeness gate, and for the
same reason: a silent no-op replace is indistinguishable from a successful one.

STRUCTURAL PARSE GUARD: every `.json` file and every `.jsonl` line that parsed
BEFORE redaction must still parse after. If not, the affected files are restored
from their pre-write contents and the run exits 1. This guard is independent of
the patterns, which is the point: it caught a value class of `\S+` that consumed
a JSON string's closing quote and every field after it, turning a redaction into
silent data destruction that both text-level scans reported as success. Any
future rule that eats structure fails here rather than in a reader's hands.

--dry-run RUNS EVERY CHECK -- patterns, misses, parse guard, and a readback
simulation against the candidate text -- and returns the SAME exit status as a
real run. It differs only in not writing. A dry run that cannot fail is not a
rehearsal.

## The `sk-` boundary guard

The obvious pattern `sk-[A-Za-z0-9_-]{8,}` is wrong for this corpus. It matches
inside ordinary words: measured against the real transcripts it hit 28 times, all
of them prose -- `risk-stratify`, `risk-underwritten`, `risk-targeted`,
`risk-triggered` -- and would have replaced substrings of the evidence with
`[REDACTED-SECRET]`, corrupting the artifacts this script exists to publish. A
real key begins at a token boundary, so the pattern carries a negative lookbehind
and the same measurement now yields zero prose hits.

## Host-environment stripping

`stream.jsonl` files open with a `system`/`init` event describing the machine
rather than the run. Its `session_id`, `uuid`, `plugins`, `skills`,
`slash_commands` and `mcp_servers` values are replaced with
`[REDACTED-HOST-ENV]`; `claude_code_version`, `model` and `tools` are kept
because they are evidence. This rule is structural (parse, replace values,
re-serialise) rather than textual, and only rewrites a line whose values actually
changed, so everything else stays byte-identical.

## Out of scope, deliberately

Only the shapes listed in `SECRET_PATTERNS` are redacted: OpenAI/Anthropic-style
`sk-` keys, `Bearer` tokens, `*_API_KEY=` assignments, and email addresses.

**AWS-style credentials (`AKIA...`), Google API keys (`AIza...`) and GitHub
tokens (`ghp_`/`gho_`/`ghs_`) are NOT redacted.** They are not expected in CLI
transcripts and no rule here removes them. They are instead *scanned for* and
reported as MISSES with file and line, exiting 2 -- so an unhandled shape is a
loud failure to be fixed here, never a silent pass. Exit 2 is distinct from the
readback failure (exit 1) so the two are separable in CI.
"""
from __future__ import annotations
import argparse, json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Allowlist -- see module docstring. Anything not named here is not published.
COPY_NAMES = {"response.md", "timing.json", "grading.json",
              "stream.jsonl", "stderr.txt", "judge.json"}

REDACTED_USER = "/Users/REDACTED"
SECRET = "[REDACTED-SECRET]"
EMAIL = "[REDACTED-EMAIL]"

# Applied in order. The specific home directory first so it is caught with or
# without a trailing slash; the generic rule then normalises every other user.
PATH_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"/Users/kpendergast"), REDACTED_USER),
    # `REDACTED` is excluded from the name class so an already-redacted path is
    # not counted as a replacement on a second pass -- that is what makes the
    # reported counts mean "work done" rather than "rules that still match".
    (re.compile(r"/Users/(?!REDACTED/)[^/\s\"'\\]+/"), REDACTED_USER + "/"),
]

SECRET_PATTERNS: list[tuple[re.Pattern, str]] = [
    # Token-boundary guarded -- see the docstring. Covers sk-, sk-ant-, sk-proj-.
    (re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{8,}"), SECRET),
    # The value classes exclude quotes, commas, braces and whitespace. `\S+`
    # here consumed everything to end of line: in JSON that swallowed the
    # closing quote and every following field, so a redaction destroyed the
    # record it was cleaning. The structural guard below now catches that
    # class of bug regardless of the pattern; this stops causing it.
    (re.compile(r"Bearer\s+[A-Za-z0-9_\-./+=]{8,}"), SECRET),
    (re.compile(r"[A-Za-z0-9_]*_API_KEY\s*=\s*[A-Za-z0-9_\-./+=]+"), SECRET),
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), EMAIL),
]

RULES = PATH_PATTERNS + SECRET_PATTERNS

# ---------------------------------------------------- host-environment stripping
# The Claude CLI opens a `stream.jsonl` with a `{"type":"system","subtype":"init"}`
# event describing the MACHINE, not the run: which plugins and skills were
# installed, which MCP servers were connected, and two identifiers for the
# session. None of it is a secret and none of it matches a secret pattern, so the
# regex rules above leave it untouched -- but it is the operator's local
# configuration and it has no evidentiary role. The fields that DO carry evidence
# (`claude_code_version`, `model`, `tools`) are kept: `tools` in particular is what
# makes "the Skill tool was never called" checkable against the stream.
#
# This rule is structural rather than textual. It parses the line and replaces
# whole values, because a regex over serialised JSON would have to model nesting
# and would silently under-match the day the CLI changes its field order.
STREAM_NAME = "stream.jsonl"
HOST_ENV_KEYS = ("session_id", "uuid", "plugins", "skills", "slash_commands",
                 "mcp_servers")
HOST_ENV = "[REDACTED-HOST-ENV]"


def _is_init(d: object) -> bool:
    return (isinstance(d, dict) and d.get("type") == "system"
            and d.get("subtype") == "init")


def redact_init_event(text: str) -> tuple[str, int]:
    """Strip host-environment fields from any init event in a JSONL stream.

    Only lines that PARSE as an init event are touched, and a line is rewritten
    only when a value actually changed -- so every other line, and every stream
    without an init event, is preserved byte for byte. Re-serialised with
    `separators=(",", ":")`, which round-trips the CLI's own compact encoding
    exactly (verified against the committed streams).
    """
    out, n = [], 0
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        if body.startswith("{") and '"init"' in body:
            try:
                d = json.loads(body)
            except ValueError:
                out.append(line); continue
            if _is_init(d):
                hits = [k for k in HOST_ENV_KEYS if k in d and d[k] != HOST_ENV]
                if hits:
                    for k in hits:
                        d[k] = HOST_ENV
                    n += len(hits)
                    out.append(json.dumps(d, separators=(",", ":"),
                                          ensure_ascii=False)
                               + line[len(body):])
                    continue
        out.append(line)
    return "".join(out), n


def surviving_host_env(text: str) -> list[str]:
    """Host-env keys still carrying a real value in an init event. Readback."""
    bad = []
    for line in text.splitlines():
        body = line.strip()
        if not (body.startswith("{") and '"init"' in body):
            continue
        try:
            d = json.loads(body)
        except ValueError:
            continue
        if _is_init(d):
            bad += [k for k in HOST_ENV_KEYS if k in d and d[k] != HOST_ENV]
    return bad


# Known-secret shapes this script does NOT handle. Found => reported, exit 2.
OUT_OF_SCOPE: list[tuple[str, re.Pattern]] = [
    ("aws-access-key-id", re.compile(r"AKIA[A-Z0-9]{16}")),
    ("google-api-key", re.compile(r"AIza[A-Za-z0-9_-]{35}")),
    ("github-token", re.compile(r"gh[posu]_[A-Za-z0-9]{20,}")),
]


def _rel(p: Path) -> str:
    """Display path. `Path.relative_to` RAISES for a tree outside the repo root,
    which `--root` and `--copy-from` both permit, so a progress line must not be
    the thing that ends the run."""
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def redact(text: str, name: str | None = None) -> tuple[str, dict[str, int]]:
    """Apply every rule. Returns (redacted_text, {rule: n_replacements}).

    `name` is the file's basename. The structural init-event rule applies only to
    `stream.jsonl`; the textual rules apply everywhere. Structural first, so the
    textual rules are not counted against values that are about to be discarded
    wholesale.
    """
    counts: dict[str, int] = {}
    if name == STREAM_NAME:
        text, n = redact_init_event(text)
        if n:
            counts["init-event host-env"] = n
    for pat, repl in RULES:
        text, n = pat.subn(repl, text)
        if n:
            counts[pat.pattern] = counts.get(pat.pattern, 0) + n
    return text, counts


def residual(text: str, name: str | None = None) -> list[tuple[str, str]]:
    """Matches that survived redaction. Non-empty means the write is unusable."""
    out = [(pat.pattern, m) for pat, _ in RULES for m in pat.findall(text)]
    if name == STREAM_NAME:
        out += [("init-event host-env", k) for k in surviving_host_env(text)]
    return out


def out_of_scope_hits(text: str) -> list[tuple[str, int, str]]:
    """(label, 1-indexed line, match) for every known-secret shape we do not
    handle. Reported rather than removed -- see the module docstring."""
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        for label, pat in OUT_OF_SCOPE:
            hits += [(label, i, m) for m in pat.findall(line)]
    return hits


# ------------------------------------------------------- structural parse guard
# A redaction that produces invalid JSON has destroyed evidence, and neither the
# residual scan nor the miss scan can see it: both operate on text. This guard is
# structural and pattern-independent -- it asserts that anything which parsed
# before still parses after, so a future rule that eats a closing quote fails the
# run instead of silently truncating a record.

def parse_shape(path: Path, text: str) -> object | None:
    """What parsed BEFORE redaction. `None` for files this guard does not model.

    A whole-file bool for `.json`; the set of line numbers that parsed for
    `.jsonl`. Lines that did not parse to begin with are not this guard's
    business -- it checks for regressions, not for pre-existing malformity.
    """
    if path.suffix == ".json":
        try:
            json.loads(text); return True
        except ValueError:
            return False
    if path.suffix == ".jsonl":
        ok = set()
        for i, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                json.loads(line); ok.add(i)
            except ValueError:
                pass
        return ok
    return None


def parse_regressions(path: Path, before: object | None, text: str) -> list[str]:
    """Locations that parsed before and do not parse now."""
    if before is None:
        return []
    after = parse_shape(path, text)
    if path.suffix == ".json":
        return [] if after or not before else [f"{_rel(path)}: whole file"]
    return [f"{_rel(path)}:{i}" for i in sorted(set(before) - set(after))]


def copy_tree(src: Path, dst: Path, dry_run: bool) -> int:
    """Mirror the allowlisted files from src into dst, preserving relative paths."""
    n = 0
    for f in sorted(src.rglob("*")):
        if not f.is_file() or f.name not in COPY_NAMES:
            continue
        target = dst / f.relative_to(src)
        n += 1
        if dry_run:
            print(f"  would copy  {_rel(target)}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target)
    print(f"{'would copy' if dry_run else 'copied'} {n} files "
          f"({', '.join(sorted(COPY_NAMES))})")
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default="evals/transcripts",
                    help="tree to redact, relative to the repo root")
    ap.add_argument("--copy-from", default=None,
                    help="mirror the allowlisted files from this tree first "
                         "(e.g. evals-workspace)")
    ap.add_argument("--dry-run", action="store_true",
                    help="run every check and return the same exit status as a "
                         "real run; differ only in not writing")
    args = ap.parse_args()

    dst = ROOT / args.root
    if args.copy_from:
        src = ROOT / args.copy_from
        if not src.is_dir():
            print(f"no such source tree: {src}", file=sys.stderr); return 1
        copy_tree(src, dst, args.dry_run)
    if not dst.is_dir():
        print(f"no such tree: {dst}", file=sys.stderr); return 1

    files = sorted(f for f in dst.rglob("*") if f.is_file() and f.name in COPY_NAMES)
    total, changed_files, misses, broke, written = 0, 0, [], [], []

    for f in files:
        original = f.read_text(encoding="utf-8", errors="surrogateescape")
        before = parse_shape(f, original)
        text, counts = redact(original, f.name)
        n = sum(counts.values())
        misses += [(f, *h) for h in out_of_scope_hits(text)]
        # Structural guard, evaluated on the candidate text -- BEFORE it is
        # written, so --dry-run reaches exactly the same verdict as a real run.
        broke += [(f, loc) for loc in parse_regressions(f, before, text)]
        if n:
            changed_files += 1
            total += n
            detail = ", ".join(f"{k} x{v}" for k, v in sorted(counts.items()))
            print(f"  {'would redact' if args.dry_run else 'redacted'} "
                  f"{_rel(f)}: {n} ({detail})")
        if args.dry_run or text == original:
            continue
        f.write_text(text, encoding="utf-8", errors="surrogateescape")
        written.append((f, original))

    verb = "would change" if args.dry_run else "changed"
    print(f"{verb} {changed_files}/{len(files)} files, {total} replacements")

    # A redaction that produced invalid JSON destroyed evidence. Roll the
    # affected files back to their pre-write contents and fail.
    if broke:
        for f, original in written:
            f.write_text(original, encoding="utf-8", errors="surrogateescape")
        print(f"\nPARSE GUARD FAILED: redaction broke {len(broke)} location(s) "
              f"that parsed beforehand"
              + ("" if args.dry_run else
                 f"; restored {len(written)} file(s) from the pre-write copy"),
              file=sys.stderr)
        for f, loc in broke[:20]:
            print(f"  {loc}", file=sys.stderr)
        return 1

    # Readback assertion: re-read from disk on a real run, never trust the write.
    # Under --dry-run the same scan runs against the candidate text, so the
    # simulated verdict matches what a real run would produce.
    failed = []
    for f in files:
        text = (redact(f.read_text(encoding="utf-8", errors="surrogateescape"),
                       f.name)[0] if args.dry_run else
                f.read_text(encoding="utf-8", errors="surrogateescape"))
        failed += [(f, pattern, match) for pattern, match in residual(text, f.name)]
    if failed:
        print(f"\nREADBACK {'SIMULATION ' if args.dry_run else ''}FAILED: "
              f"{len(failed)} pattern(s) still match after "
              f"{'a simulated write' if args.dry_run else 'writing'}:",
              file=sys.stderr)
        for f, pattern, match in failed[:20]:
            print(f"  {_rel(f)}: /{pattern}/ -> {match!r}", file=sys.stderr)
        return 1
    print(f"parse guard OK: no location that parsed before fails after")
    print(f"readback{' (simulated)' if args.dry_run else ''} OK: 0 of {len(RULES)} "
          f"patterns match across {len(files)} files")

    if misses:
        print(f"\nMISSES: {len(misses)} known-secret shape(s) this script does "
              "NOT redact (see the docstring -- out of scope, not silently "
              "passed):", file=sys.stderr)
        for f, label, line, match in misses[:20]:
            print(f"  {_rel(f)}:{line}: {label} -> {match!r}",
                  file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
