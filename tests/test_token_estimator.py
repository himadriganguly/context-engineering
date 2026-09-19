import os
import sys
import pytest

# Add the scripts directory to the Python path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../skills/context-engineering/scripts')))

from token_estimator import estimate_tokens, estimate_file, DEFAULT_CHARS_PER_TOKEN

def test_estimate_tokens_heuristic(monkeypatch):
    """Ensure the fallback heuristic correctly divides characters."""
    import token_estimator
    
    # Force the module to use the character heuristic
    monkeypatch.setattr(token_estimator, "HAS_TIKTOKEN", False)
    
    # 38 characters / 3.8 chars_per_token = exactly 10 tokens
    text = "A" * 38
    assert estimate_tokens(text, DEFAULT_CHARS_PER_TOKEN) == 10
    
    # Empty strings must safely return 0
    assert estimate_tokens("", DEFAULT_CHARS_PER_TOKEN) == 0

def test_estimate_tokens_exact():
    """Ensure exact tiktoken math is used when the dependency is present."""
    try:
        import tiktoken
    except ImportError:
        pytest.skip("tiktoken is not installed in this test environment")
        
    import token_estimator
    token_estimator.HAS_TIKTOKEN = True
    
    text = "Hello, world!"
    # 'Hello, world!' encodes to exactly 4 tokens in cl100k_base
    assert estimate_tokens(text, DEFAULT_CHARS_PER_TOKEN) == 4

def test_estimate_file(tmp_path, monkeypatch):
    """Ensure files are read correctly and estimated."""
    import token_estimator
    monkeypatch.setattr(token_estimator, "HAS_TIKTOKEN", False)
    
    test_file = tmp_path / "sample.txt"
    test_file.write_text("A" * 76, encoding="utf-8")
    
    # 76 characters / 3.8 chars_per_token = exactly 20 tokens
    assert estimate_file(str(test_file), DEFAULT_CHARS_PER_TOKEN) == 20

def test_estimate_file_invalid_encoding(tmp_path, monkeypatch):
    """Ensure non-UTF-8 files are handled via the errors='replace' fallback."""
    import token_estimator
    monkeypatch.setattr(token_estimator, "HAS_TIKTOKEN", False)
    
    test_file = tmp_path / "binary_mock.bin"
    # Write raw bytes that invalidate standard UTF-8 decoding
    test_file.write_bytes(b"\xff\xfe\x00\x00")
    
    # Should not throw a UnicodeDecodeError
    tokens = estimate_file(str(test_file), DEFAULT_CHARS_PER_TOKEN)
    assert tokens > 0