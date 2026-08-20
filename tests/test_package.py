"""Guards on the release packager's layout assertions and its reproducibility.

Two hosts demand incompatible zip roots -- claude.ai wants the skill folder as
the root, Perplexity's Computer skill upload wants `SKILL.md` itself at the root
-- and getting either wrong fails at *upload* time, on someone else's machine,
with a generic host error that never says "your zip root is wrong". The
assertions in build/package.py are the only thing standing between a wrong-rooted
asset and a published release, so they are tested the way the generator's
refusals are: by handing each one the mistake it exists to catch.

The positive control is not ceremony. Four assertions that all raise would pass
every negative test here while rejecting the real assets too.
"""
from __future__ import annotations

import zipfile

import pytest

FOLDER_ROOT = "innovate-or-die"


def _build(package, tmp_path, prefix, name):
    """A real `git archive` of HEAD, restamped, exactly as a release would be."""
    out = tmp_path / name
    package.archive("HEAD", out, prefix)
    package.restamp(out, (2026, 1, 1, 0, 0, 0))
    return out


# ------------------------------------------------------ wrong root, both ways

def test_flat_zip_is_rejected_when_the_folder_root_layout_is_expected(package, tmp_path):
    """The claude.ai asset built flat: upload succeeds at the API level and the
    skill never loads, because nothing sits where the host looks for it."""
    z = _build(package, tmp_path, None, "flat.zip")
    with pytest.raises(SystemExit) as e:
        package.assert_layout(z, FOLDER_ROOT)
    assert "innovate-or-die/SKILL.md" in str(e.value)


def test_folder_zip_is_rejected_when_the_flat_layout_is_expected(package, tmp_path):
    """The mirror image: the Perplexity asset built with the folder wrapper."""
    z = _build(package, tmp_path, FOLDER_ROOT, "folder.zip")
    with pytest.raises(SystemExit) as e:
        package.assert_layout(z, None)
    assert "SKILL.md is not at 'SKILL.md'" in str(e.value)


def test_skill_md_below_depth_one_is_rejected(package, tmp_path):
    """`SKILL.md` inside the right root but one level too deep. The prefix check
    alone would accept this, which is why depth is asserted separately."""
    z = _build(package, tmp_path, f"{FOLDER_ROOT}/nested", "nested.zip")
    with pytest.raises(SystemExit) as e:
        package.assert_layout(z, FOLDER_ROOT)
    assert "SKILL.md" in str(e.value)


# --------------------------------------------------------- a member goes missing

def test_a_dropped_member_is_rejected_and_named(package, tmp_path):
    """A file silently absent from the package is the failure mode with no
    symptom: the skill loads, and the critic's brief is simply not there."""
    full = _build(package, tmp_path, FOLDER_ROOT, "full.zip")
    short = tmp_path / "short.zip"
    with zipfile.ZipFile(full) as src, zipfile.ZipFile(short, "w") as dst:
        for info in src.infolist():
            if not info.filename.endswith("roles/critic.md"):
                dst.writestr(info, src.read(info.filename))

    with pytest.raises(SystemExit) as e:
        package.assert_layout(short, FOLDER_ROOT)
    msg = str(e.value)
    assert "roles/critic.md" in msg, "the failure must name the file that vanished"
    assert "missing=" in msg


# ------------------------------------------------------------ positive control

def test_both_real_layouts_are_accepted(package, tmp_path):
    """Without this the four tests above would pass an assert_layout() that
    rejected everything, including the assets we actually ship."""
    package.assert_layout(_build(package, tmp_path, FOLDER_ROOT, "a.zip"), FOLDER_ROOT)
    package.assert_layout(_build(package, tmp_path, None, "b.zip"), None)


# ------------------------------------------------------------ reproducibility

def test_two_builds_of_the_same_ref_are_byte_identical(package, tmp_path):
    """A published checksum is only meaningful if the asset can be rebuilt.

    `git archive` given a `<ref>:<path>` argument resolves a TREE, which carries
    no date, so it stamps members with the wall clock -- and it writes a second
    Unix mtime into an `UT` extra field that no listing shows. Both are why
    restamp() exists; drop it and this test fails on the timestamps.
    """
    _sha, _version, when = package.resolve("HEAD")

    built = []
    for name in ("first.zip", "second.zip"):
        out = tmp_path / name
        package.archive("HEAD", out, FOLDER_ROOT)
        package.restamp(out, when)
        built.append(out)

    assert built[0].read_bytes() == built[1].read_bytes()

    for info in zipfile.ZipFile(built[0]).infolist():
        assert info.date_time == when, "member mtime must come from the commit, not the clock"
        assert info.extra == b"", "the UT extra field carries a second, build-time mtime"
