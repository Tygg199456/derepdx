import os
import pathlib
import subprocess
import sys

from derepdx.fixtures import fixture

SRC = str(pathlib.Path(__file__).resolve().parent.parent / "src")
ENV = {**os.environ, "PYTHONPATH": SRC}


def run_cli(*args):
    return subprocess.run([sys.executable, "-m", "derepdx.cli", *args],
                          capture_output=True, text=True, env=ENV)


def test_version():
    p = run_cli("--version")
    assert p.returncode == 0
    assert "derepdx" in p.stdout


def test_positive_fixture_exits_one():
    p = run_cli("check-length", str(fixture("length", "pos_same_strain_107kb.tsv")))
    assert p.returncode == 1
    assert "LENGTH_MISMATCH" in p.stdout


def test_negative_fixture_exits_zero():
    p = run_cli("check-length", str(fixture("length", "neg_same_strain_within_tol.tsv")))
    assert p.returncode == 0
    assert "[PASS]" in p.stdout


def test_bad_input_exits_two():
    p = run_cli("check-length", "/nonexistent/file.tsv")
    assert p.returncode == 2


def test_schema_error_exits_two(tmp_path):
    bad = tmp_path / "bad.tsv"
    bad.write_text("accession\ttotal_bp\nA\t1\n")  # missing 'strain'
    p = run_cli("check-length", str(bad))
    assert p.returncode == 2
    assert "strain" in p.stderr


def test_json_output_is_machine_readable():
    import json
    p = run_cli("check-length", str(fixture("length", "pos_same_strain_107kb.tsv")), "--json")
    payload = json.loads(p.stdout)
    assert payload["ok"] is False
    assert payload["findings"][0]["code"] == "LENGTH_MISMATCH"


def test_demo_runs_and_passes():
    p = run_cli("demo")
    assert p.returncode == 0, p.stdout + p.stderr
    assert "positive" in p.stdout
