"""Guards on the transcript redactor.

Two things this has to get right, and they pull against each other:

* remove every local identifier, verified by re-reading from disk rather than by
  trusting the write; and
* not damage the evidence in the process. The obvious `sk-[A-Za-z0-9_-]{8,}`
  pattern matched 28 times against the real transcripts and every hit was prose
  -- `risk-stratify`, `risk-underwritten`, `risk-targeted`, `risk-triggered`.
  Redacting those would have silently corrupted the artifacts being published,
  and the readback assertion would have reported success. That case is pinned
  below.
"""
from __future__ import annotations

import json
import re

import pytest

# One string carrying every shape the script claims to handle.
DIRTY = """\
home: /Users/kpendergast/.claude/plugins/cache/x
other: /Users/someoneelse/projects/thing.md
trailing: /Users/kpendergast
openai: sk-abcdefghijklmnop1234
anthropic: sk-ant-api03-AAAAAAAABBBBBBBBCCCCCCCC
project: sk-proj-ZZZZZZZZYYYYYYYYXXXXXXXX
header: Bearer eyJhbGciOiJIUzI1NiJ9abcdefg
env: ANTHROPIC_API_KEY=sk-ant-secretvaluehere
mail: ken@pestalytix.com
"""

# The prose that the naive pattern destroyed. Must survive byte-for-byte.
PROSE = ("Risk-stratify the accounts, use risk-underwritten pricing, apply "
         "risk-targeted outreach, and add a risk-triggered escalation.")


def write_tree(root, files):
    """files: {relative path: text}. Only allowlisted basenames are read back."""
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return root


# --------------------------------------------------------------- unit: patterns

def test_every_declared_pattern_is_replaced(redact):
    out, counts = redact.redact(DIRTY)
    assert "/Users/kpendergast" not in out
    assert "/Users/someoneelse" not in out
    assert out.count("/Users/REDACTED") == 3
    assert "sk-abcdefghijklmnop1234" not in out
    assert "sk-ant-api03-AAAAAAAABBBBBBBBCCCCCCCC" not in out
    assert "sk-proj-ZZZZZZZZYYYYYYYYXXXXXXXX" not in out
    assert "Bearer" not in out
    assert "secretvaluehere" not in out
    assert "ken@pestalytix.com" not in out
    assert "[REDACTED-EMAIL]" in out
    assert out.count("[REDACTED-SECRET]") == 5, out
    # The VARIABLE NAME survives; only its value is redacted. That is the point
    # of the constrained value class: `[` is not in it, so once the `sk-` rule
    # has replaced the value the `_API_KEY=` rule correctly declines to eat the
    # `[REDACTED-SECRET]` token and everything after it.
    assert "ANTHROPIC_API_KEY=[REDACTED-SECRET]" in out
    assert sum(counts.values()) == 9, counts


def test_nothing_survives_the_residual_scan(redact):
    assert redact.residual(redact.redact(DIRTY)[0]) == []


def test_redaction_is_idempotent(redact):
    once, _ = redact.redact(DIRTY)
    twice, counts = redact.redact(once)
    assert twice == once
    assert counts == {}, "a second pass must be a no-op, not a re-mangle"


def test_an_already_redacted_path_is_not_recounted(redact):
    """`/Users/REDACTED/` still matches the generic user-path shape. If the rule
    counted it, every re-run would report phantom work."""
    out, counts = redact.redact("/Users/REDACTED/.claude/x")
    assert out == "/Users/REDACTED/.claude/x"
    assert counts == {}


# ------------------------------------------- the regression the naive pattern hit

def test_risk_prose_is_not_mistaken_for_an_api_key(redact):
    """28 real hits in the published corpus, all false positives."""
    out, counts = redact.redact(PROSE)
    assert out == PROSE
    assert counts == {}


@pytest.mark.parametrize("word", ["risk-stratify", "Risk-underwritten",
                                  "risk-targeted", "risk-triggered",
                                  "risk-management", "disk-utilisation"])
def test_sk_inside_a_word_is_never_redacted(redact, word):
    assert redact.redact(word)[0] == word


@pytest.mark.parametrize("prefix", ["", " ", "\n", "=", '"', "(", ": "])
def test_a_real_key_at_a_token_boundary_is_still_caught(redact, prefix):
    """The guard must not be so tight that it misses keys in JSON or prose."""
    out, _ = redact.redact(prefix + "sk-ant-api03-REALKEYMATERIAL1234")
    assert "REALKEYMATERIAL" not in out
    assert "[REDACTED-SECRET]" in out


# ------------------------------------------------------- end to end through main

@pytest.fixture
def run(tmp_path, redact, monkeypatch):
    def go(files, argv_extra=()):
        write_tree(tmp_path / "evals/transcripts", files)
        monkeypatch.setattr(redact, "ROOT", tmp_path)
        monkeypatch.setattr("sys.argv",
                            ["redact_transcripts.py", *argv_extra])
        rc = redact.main()
        got = {rel: (tmp_path / "evals/transcripts" / rel).read_text(encoding="utf-8")
               for rel in files}
        return rc, got
    return go


def test_clean_run_exits_zero_and_readback_passes(run):
    rc, got = run({"iteration-1/p/t/case/with_skill/outputs/response.md": DIRTY,
                   "iteration-1/p/t/case/with_skill/timing.json":
                       json.dumps({"cwd": "/Users/kpendergast/tmp"})})
    assert rc == 0
    for text in got.values():
        assert "kpendergast" not in text
    assert "/Users/REDACTED/tmp" in got["iteration-1/p/t/case/with_skill/timing.json"]


def test_json_stays_parseable_after_redaction(run):
    rel = "iteration-1/p/t/case/with_skill/timing.json"
    rc, got = run({rel: json.dumps(
        {"cwd": "/Users/kpendergast/T/x", "who": "ken@pestalytix.com",
         "note": "risk-stratify the accounts"})})
    assert rc == 0
    d = json.loads(got[rel])           # the replacements must not break the JSON
    assert d["cwd"] == "/Users/REDACTED/T/x"
    assert d["who"] == "[REDACTED-EMAIL]"
    assert d["note"] == "risk-stratify the accounts"


def test_dry_run_writes_nothing(run):
    rel = "iteration-1/p/t/case/with_skill/outputs/response.md"
    rc, got = run({rel: DIRTY}, argv_extra=("--dry-run",))
    assert rc == 0
    assert got[rel] == DIRTY, "--dry-run must leave the tree untouched"


def test_files_outside_the_allowlist_are_not_touched(run):
    rel = "iteration-1/p/t/case/with_skill/scratch-notes.md"
    rc, got = run({rel: DIRTY,
                   "iteration-1/p/t/case/with_skill/timing.json": "{}"})
    assert rc == 0
    assert got[rel] == DIRTY, "the allowlist governs reading as well as copying"


# --------------------------------------------- out-of-scope shapes are reported

def test_aws_style_key_is_reported_as_a_miss_not_silently_passed(run, capsys):
    """AKIA/AIza/gh*_ are documented out of scope. Out of scope must mean loud,
    not invisible: exit 2, distinct from the readback failure's exit 1."""
    rel = "iteration-1/p/t/case/with_skill/outputs/response.md"
    rc, got = run({rel: "leaked: AKIAIOSFODNN7EXAMPLE\n"})
    assert rc == 2
    err = capsys.readouterr().err
    assert "MISSES" in err
    assert "aws-access-key-id" in err
    assert "AKIAIOSFODNN7EXAMPLE" in err
    assert f"{rel}:1" in err, "a miss must name the file and line"
    assert "AKIAIOSFODNN7EXAMPLE" in got[rel], (
        "the script reports the shape; it does not claim to remove it")


@pytest.mark.parametrize("label,secret", [
    ("aws-access-key-id", "AKIAIOSFODNN7EXAMPLE"),
    ("google-api-key", "AIza" + "B" * 35),
    ("github-token", "ghp_" + "C" * 24),
])
def test_each_out_of_scope_shape_is_detected(redact, label, secret):
    hits = redact.out_of_scope_hits(f"x = {secret}")
    assert [(l, n) for l, n, _ in hits] == [(label, 1)]


def test_a_clean_corpus_reports_no_misses(redact):
    assert redact.out_of_scope_hits(DIRTY + PROSE) == []


# -------------------------------------------------------------- the copy allowlist

def test_copy_takes_only_the_allowlisted_artifact_kinds(tmp_path, redact):
    src = write_tree(tmp_path / "src", {
        "iteration-1/p/t/case/with_skill/outputs/response.md": "a",
        "iteration-1/p/t/case/with_skill/timing.json": "{}",
        "iteration-1/p/t/case/with_skill/grading.json": "{}",
        "iteration-1/p/t/case/with_skill/trace/stream.jsonl": "{}",
        "iteration-1/p/t/case/with_skill/trace/stderr.txt": "",
        "iteration-1/judge.json": '{"verdicts":[]}',
        "iteration-1/p/t/case/with_skill/SCRATCH.md": "do not publish",
        "iteration-1/benchmark.json": "do not publish",
    })
    dst = tmp_path / "dst"
    n = redact.copy_tree(src, dst, dry_run=False)
    assert n == len(redact.COPY_NAMES) == 6
    copied = {p.name for p in dst.rglob("*") if p.is_file()}
    assert copied == redact.COPY_NAMES
    assert (dst / "iteration-1/judge.json").exists(), "judge.json is published"
    assert not (dst / "iteration-1/benchmark.json").exists(), (
        "benchmark.json is reproduced verbatim inside each results file")
    assert not (dst / "iteration-1/p/t/case/with_skill/SCRATCH.md").exists()


def test_copy_preserves_the_relative_tree(tmp_path, redact):
    src = write_tree(tmp_path / "src",
                     {"iteration-3/codex/workhorse/eval-x/with_skill/timing.json": "{}"})
    dst = tmp_path / "dst"
    redact.copy_tree(src, dst, dry_run=False)
    assert (dst / "iteration-3/codex/workhorse/eval-x/with_skill/timing.json").exists()


def test_copy_dry_run_creates_nothing(tmp_path, redact):
    src = write_tree(tmp_path / "src",
                     {"iteration-1/p/t/c/with_skill/timing.json": "{}"})
    dst = tmp_path / "dst"
    assert redact.copy_tree(src, dst, dry_run=True) == 1
    assert not dst.exists()


# ------------------------------------------- init-event host-environment strip

INIT = {"type": "system", "subtype": "init",
        "cwd": "/tmp/iod-with_skill-abc",
        "session_id": "0f2211c2-a425-4366-bd56-3d6c35ba9da6",
        "uuid": "c4839b80-aab8-4d47-9d5f-52e498dc7035",
        "tools": ["Task", "Bash", "Skill", "WebSearch"],
        "mcp_servers": [{"name": "wordpress-mcp", "status": "pending"},
                        {"name": "bigquery", "status": "pending"}],
        "model": "claude-sonnet-5",
        "slash_commands": ["pestalytix-media-exif", "innovate-or-die"],
        "skills": ["pestalytix-media-exif", "innovate-or-die"],
        "plugins": [{"name": "frontend-design",
                     "path": "/Users/REDACTED/.claude/plugins/cache/x",
                     "source": "frontend-design@claude-plugins-official"}],
        "claude_code_version": "2.1.218",
        "agents": ["claude", "Explore"],
        "apiKeySource": "none"}

STRIPPED = ("session_id", "uuid", "plugins", "skills", "slash_commands",
            "mcp_servers")
KEPT = ("claude_code_version", "model", "tools")


def stream(*events):
    return "".join(json.dumps(e, separators=(",", ":")) + "\n" for e in events)


def test_host_env_values_are_replaced(redact):
    out, n = redact.redact_init_event(stream(INIT))
    d = json.loads(out)
    assert n == len(STRIPPED) == 6
    for k in STRIPPED:
        assert d[k] == "[REDACTED-HOST-ENV]", k


def test_evidence_fields_are_kept_verbatim(redact):
    """`tools` in particular: it is what makes 'the Skill tool was never called'
    checkable against the stream rather than merely asserted."""
    d = json.loads(redact.redact_init_event(stream(INIT))[0])
    for k in KEPT:
        assert d[k] == INIT[k], k
    assert "Skill" in d["tools"]


def test_unnamed_fields_are_left_alone(redact):
    d = json.loads(redact.redact_init_event(stream(INIT))[0])
    for k in ("cwd", "agents", "apiKeySource", "type", "subtype"):
        assert d[k] == INIT[k], k


def test_the_identifying_values_are_actually_gone(redact):
    out, _ = redact.redact_init_event(stream(INIT))
    for leaked in ("wordpress-mcp", "bigquery", "pestalytix-media-exif",
                   "frontend-design@claude-plugins-official",
                   "0f2211c2-a425-4366-bd56-3d6c35ba9da6",
                   "c4839b80-aab8-4d47-9d5f-52e498dc7035"):
        assert leaked not in out, leaked


def test_init_strip_is_idempotent(redact):
    once, n1 = redact.redact_init_event(stream(INIT))
    twice, n2 = redact.redact_init_event(once)
    assert twice == once
    assert (n1, n2) == (6, 0), "a second pass must report no work"


def test_non_init_lines_are_byte_identical(redact):
    other = {"type": "assistant", "message": {"content": [{"text": "risk-tiered"}]}}
    text = stream(INIT, other, {"type": "result", "session_id": "keep-me"})
    out, _ = redact.redact_init_event(text)
    assert out.splitlines()[1:] == text.splitlines()[1:]
    # `session_id` outside an init event is not this rule's business.
    assert "keep-me" in out


def test_a_stream_with_no_init_event_is_untouched(redact):
    text = stream({"type": "assistant", "session_id": "x", "plugins": ["y"]})
    assert redact.redact_init_event(text) == (text, 0)


def test_a_malformed_line_does_not_crash_the_pass(redact):
    text = '{"type":"system","subtype":"init" TRUNCATED\n' + stream(INIT)
    out, n = redact.redact_init_event(text)
    assert n == 6, "the valid init event is still processed"
    assert out.splitlines()[0] == '{"type":"system","subtype":"init" TRUNCATED'


def test_the_rule_applies_only_to_stream_jsonl(redact):
    """A `timing.json` that happened to contain an init-shaped line is not a
    stream, and the structural rule must not reach into it."""
    text = stream(INIT)
    assert redact.redact(text, "timing.json")[0] == text
    assert "init-event host-env" in redact.redact(text, "stream.jsonl")[1]


def test_residual_flags_an_unstripped_init_event(redact):
    """Readback has to know about the structural rule too, or a failed
    structural pass reports success."""
    text = stream(INIT)
    assert sorted(redact.surviving_host_env(text)) == sorted(STRIPPED)
    assert redact.residual(text, "stream.jsonl"), "must be caught as residual"
    assert redact.residual(text, "timing.json") == [], "not a stream; not its rule"
    clean = redact.redact_init_event(text)[0]
    assert redact.residual(clean, "stream.jsonl") == []


def test_end_to_end_strips_a_stream_and_passes_readback(run):
    rel = "iteration-1/p/t/case/with_skill/trace/stream.jsonl"
    rc, got = run({rel: stream(INIT, {"type": "result", "result": "risk-tiered"})})
    assert rc == 0
    d = json.loads(got[rel].splitlines()[0])
    assert all(d[k] == "[REDACTED-HOST-ENV]" for k in STRIPPED)
    assert d["tools"] == INIT["tools"]
    assert "risk-tiered" in got[rel], "the evidence is not collateral damage"


# ---------------------------------------------- structural parse guard (ITEM 1)

REVIEWER = '{"env":"OPENAI_API_KEY=sk-abcdefghijklmnop","keep":"evidence"}'


def test_the_reviewers_input_redacts_to_valid_json_with_evidence_intact(redact):
    """`\\S+` consumed the closing quote and every field after it, so redacting
    this record destroyed it while both text-level scans reported success."""
    out, _ = redact.redact(REVIEWER)
    d = json.loads(out)                      # must not raise
    assert d["keep"] == "evidence", "the evidence field must survive redaction"
    assert "sk-abcdefghijklmnop" not in out
    assert "[REDACTED-SECRET]" in out
    assert redact.residual(out) == []


@pytest.mark.parametrize("src", [
    '{"a":"Bearer abcdefghijklmnop","b":"keep"}',
    '{"a":"FOO_API_KEY=abcdefgh","b":"keep"}',
    '{"a":"x sk-abcdefghijklmnop y","b":"keep"}',
])
def test_value_classes_never_cross_a_json_boundary(redact, src):
    d = json.loads(redact.redact(src)[0])
    assert d["b"] == "keep"


def test_parse_guard_catches_a_rule_that_breaks_json(redact, tmp_path, monkeypatch):
    """The guard is pattern-independent: inject a deliberately greedy rule and it
    must fail the run even though residual() and the miss scan both pass."""
    rel = "it/p/t/c/with_skill/timing.json"
    root = tmp_path
    f = root / "evals/transcripts" / rel
    f.parent.mkdir(parents=True)
    f.write_text('{"cwd":"/Users/someone/x","keep":"evidence"}')
    greedy = (re.compile(r"/Users/[^\n]+"), "/Users/REDACTED")
    monkeypatch.setattr(redact, "RULES", [greedy])
    monkeypatch.setattr(redact, "ROOT", root)
    monkeypatch.setattr("sys.argv", ["redact_transcripts.py"])
    assert redact.main() == 1
    # and the file is restored, not left truncated
    assert json.loads(f.read_text())["keep"] == "evidence"


def test_parse_guard_reports_the_location(redact, tmp_path, monkeypatch, capsys):
    rel = "it/p/t/c/with_skill/trace/stream.jsonl"
    f = tmp_path / "evals/transcripts" / rel
    f.parent.mkdir(parents=True)
    f.write_text('{"a":1}\n{"cwd":"/Users/someone/x","keep":2}\n')
    monkeypatch.setattr(redact, "RULES", [(re.compile(r"/Users/[^\n]+"), "/Users/R")])
    monkeypatch.setattr(redact, "ROOT", tmp_path)
    monkeypatch.setattr("sys.argv", ["redact_transcripts.py"])
    assert redact.main() == 1
    err = capsys.readouterr().err
    assert "PARSE GUARD FAILED" in err
    assert f"{rel}:2" in err, "must name the failing line, not just the file"


def test_a_line_that_never_parsed_is_not_a_regression(redact, tmp_path, monkeypatch,
                                                      capsys):
    """The guard checks for REGRESSIONS, not pre-existing malformity.

    A stream carrying a line that was already unparseable must not be blocked,
    must not be reported as a regression, and must still exit 0. Otherwise one
    bad line in an archived transcript would make the whole tree unpublishable
    and there would be no way to redact it at all.
    """
    f = tmp_path / "evals/transcripts/it/p/t/c/with_skill/trace/stream.jsonl"
    f.parent.mkdir(parents=True)
    before = 'NOT JSON AT ALL\n{"cwd":"/Users/someone/x"}\n'
    f.write_text(before)

    # Only line 2 is tracked: line 1 never parsed, so it is not the guard's.
    assert redact.parse_shape(f, before) == {2}

    monkeypatch.setattr(redact, "ROOT", tmp_path)
    monkeypatch.setattr("sys.argv", ["redact_transcripts.py"])
    assert redact.main() == 0, "a pre-existing bad line must not fail the run"

    out, err = capsys.readouterr()
    assert "PARSE GUARD FAILED" not in err
    assert err == "", "nothing to report: this is not a regression"
    assert "parse guard OK" in out

    after = f.read_text()
    assert after.splitlines()[0] == "NOT JSON AT ALL", "left exactly as found"
    # Guards against a vacuous pass: the run must really have done the work,
    # not skipped the file because one of its lines was malformed.
    assert "/Users/REDACTED/x" in after
    assert redact.parse_shape(f, after) == {2}


# ------------------------------------------------- --dry-run is a real rehearsal

def _tree(tmp_path, text, name="response.md"):
    f = tmp_path / "evals/transcripts/it/p/t/c/with_skill/outputs" / name
    f.parent.mkdir(parents=True)
    f.write_text(text)
    return f


def test_dry_run_returns_the_same_status_as_a_real_run_for_misses(redact, tmp_path,
                                                                 monkeypatch):
    f = _tree(tmp_path, "leaked: AKIAIOSFODNN7EXAMPLE\n")
    monkeypatch.setattr(redact, "ROOT", tmp_path)
    monkeypatch.setattr("sys.argv", ["redact_transcripts.py", "--dry-run"])
    dry = redact.main()
    monkeypatch.setattr("sys.argv", ["redact_transcripts.py"])
    real = redact.main()
    assert dry == real == 2, "a dry run that cannot fail is not a rehearsal"
    assert "AKIA" in f.read_text()


def test_dry_run_catches_a_parse_regression_without_writing(redact, tmp_path,
                                                            monkeypatch):
    f = _tree(tmp_path, '{"cwd":"/Users/someone/x","keep":"evidence"}', "timing.json")
    before = f.read_text()
    monkeypatch.setattr(redact, "RULES", [(re.compile(r"/Users/[^\n]+"), "/Users/R")])
    monkeypatch.setattr(redact, "ROOT", tmp_path)
    monkeypatch.setattr("sys.argv", ["redact_transcripts.py", "--dry-run"])
    assert redact.main() == 1
    assert f.read_text() == before, "--dry-run must not write"


def test_dry_run_and_real_run_agree_on_a_clean_tree(redact, tmp_path, monkeypatch):
    _tree(tmp_path, "risk-stratify the accounts\n")
    monkeypatch.setattr(redact, "ROOT", tmp_path)
    monkeypatch.setattr("sys.argv", ["redact_transcripts.py", "--dry-run"])
    dry = redact.main()
    monkeypatch.setattr("sys.argv", ["redact_transcripts.py"])
    assert dry == redact.main() == 0


def test_judge_json_is_in_the_copy_allowlist(redact):
    assert "judge.json" in redact.COPY_NAMES
