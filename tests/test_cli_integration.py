import os
import subprocess
import sys
import pytest

# Define the paths to the scripts relative to the tests directory
SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../skills/context-engineering/scripts'))
AUDIT_SCRIPT = os.path.join(SCRIPTS_DIR, 'context_audit.py')
ESTIMATOR_SCRIPT = os.path.join(SCRIPTS_DIR, 'token_estimator.py')

def run_cli(script_path, args):
    """Helper to run a CLI script as a subprocess."""
    return subprocess.run(
        [sys.executable, script_path] + args,
        capture_output=True,
        text=True
    )

def test_estimator_cli_text():
    """Ensure the estimator CLI correctly processes raw text via stdout."""
    result = run_cli(ESTIMATOR_SCRIPT, ["--text", "Hello world", "--chars-per-token", "3.8"])
    
    # The script should exit cleanly and output a number
    assert result.returncode == 0
    assert result.stdout.strip().isdigit()

def test_estimator_cli_missing_args():
    """Ensure the estimator CLI fails properly when required arguments are missing."""
    result = run_cli(ESTIMATOR_SCRIPT, [])
    
    # argparse should trigger a failure exit code (usually 2 for missing mutually exclusive args)
    assert result.returncode != 0
    assert "error" in result.stderr.lower()

def test_estimator_cli_invalid_file():
    """Ensure the estimator CLI catches non-existent files."""
    result = run_cli(ESTIMATOR_SCRIPT, ["--file", "does_not_exist_xyz.txt"])
    
    # Custom logger error should trigger sys.exit(1)
    assert result.returncode == 1
    assert "does not exist" in result.stderr.lower()

def test_audit_cli_invalid_dir(tmp_path):
    """Ensure the audit CLI fails gracefully on invalid session directories."""
    invalid_dir = str(tmp_path / "missing_session")
    result = run_cli(AUDIT_SCRIPT, ["--session-dir", invalid_dir])
    
    assert result.returncode == 1
    assert "does not exist" in result.stderr.lower()

def test_audit_cli_valid_empty_dir(tmp_path):
    """Ensure the audit CLI successfully processes a valid (but empty) session directory."""
    session_dir = str(tmp_path)
    # Output directory for the JSON report
    output_dir = str(tmp_path / "audits")
    
    result = run_cli(AUDIT_SCRIPT, [
        "--session-dir", session_dir,
        "--output-dir", output_dir
    ])
    
    assert result.returncode == 0
    assert "Estimated tokens: 0" in result.stderr
    
    # Verify the JSON report was actually written to disk
    generated_reports = [f for f in os.listdir(output_dir) if f.endswith(".json")]
    assert len(generated_reports) == 1

def test_audit_cli_json_flag(tmp_path):
    """Ensure the --json flag routes raw JSON to stdout."""
    session_dir = str(tmp_path)
    output_dir = str(tmp_path / "audits")
    
    result = run_cli(AUDIT_SCRIPT, [
        "--session-dir", session_dir,
        "--output-dir", output_dir,
        "--json"
    ])
    
    assert result.returncode == 0
    # Output must be parseable JSON
    import json
    parsed = json.loads(result.stdout)
    assert "estimated_tokens" in parsed