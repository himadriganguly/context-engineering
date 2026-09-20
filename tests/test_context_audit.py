import json
import os
import sys
import pytest

# Add the scripts directory to the Python path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../skills/context_engineering/scripts')))

from context_audit import load_session, audit

# Constants for testing
CHARS_PER_TOKEN = 3.8
WINDOW_SIZE = 128000

def test_empty_directory_divide_by_zero(tmp_path):
    """Ensure an empty directory does not trigger division by zero errors."""
    artifacts = load_session(str(tmp_path))
    report = audit(artifacts, WINDOW_SIZE, CHARS_PER_TOKEN)
    
    assert report["estimated_tokens"] == 0
    assert report["utilization"] == 0.0
    assert report["stale_content_ratio"] == 0.0
    assert report["repetition_ratio"] == 0.0
    assert report["instruction_survival_rate"] == 1.0 

def test_malformed_jsonl_trap(tmp_path):
    """Ensure non-dictionary and malformed JSON lines are safely ignored."""
    conv_path = tmp_path / "conversation.jsonl"
    bad_jsonl = [
        '{"role": "user", "content": "Normal turn."}\n',
        '\n',
        '"Just a string on a line"\n',
        '[1, 2, "array instead of dict"]\n',
        '{"role": "assistant", "content": \n' # Malformed
    ]
    conv_path.write_text("".join(bad_jsonl), encoding="utf-8")
    
    artifacts = load_session(str(tmp_path))
    
    assert len(artifacts["conversation"]) == 1
    assert artifacts["conversation"][0]["role"] == "user"

def test_buried_constraint_detection(tmp_path):
    """Ensure regex captures constraints buried inside a sentence."""
    conv_path = tmp_path / "conversation.jsonl"
    turn = {
        "role": "user", 
        "content": "For this specific task, you must always return valid JSON, and please ensure that the keys are snake_case."
    }
    conv_path.write_text(json.dumps(turn) + "\n", encoding="utf-8")
    
    artifacts = load_session(str(tmp_path))
    report = audit(artifacts, WINDOW_SIZE, CHARS_PER_TOKEN)
    
    assert report["constraint_count"] > 0
    assert report["constraints_survived"] == report["constraint_count"]

def test_log_dump_repetition(tmp_path):
    """Ensure identical repeated lines trigger a high repetition ratio."""
    tool_dir = tmp_path / "tool_outputs"
    tool_dir.mkdir()
    log_path = tool_dir / "server_log.txt"
    
    repeated_line = "INFO 2026-09-19 Server started successfully and is waiting for connections.\n"
    log_path.write_text(repeated_line * 50, encoding="utf-8")
    
    artifacts = load_session(str(tmp_path))
    report = audit(artifacts, WINDOW_SIZE, CHARS_PER_TOKEN)
    
    assert report["repetition_ratio"] > 0.8

def test_tiktoken_fallback_mocked(tmp_path, monkeypatch):
    """Mock the HAS_TIKTOKEN flag to verify the fallback math executes."""
    import context_audit
    
    monkeypatch.setattr(context_audit, "HAS_TIKTOKEN", False)
    
    system_path = tmp_path / "system_prompt.txt"
    system_path.write_text("A" * 38, encoding="utf-8")
    
    artifacts = load_session(str(tmp_path))
    report = audit(artifacts, WINDOW_SIZE, CHARS_PER_TOKEN)
    
    assert report["estimated_tokens"] == 10