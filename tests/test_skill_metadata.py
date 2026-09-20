import os
import re
import yaml
import pytest

# Path to the SKILL.md file relative to this test file
SKILL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../skills/context_engineering/SKILL.md')
)
SKILL_DIR = os.path.dirname(SKILL_PATH)

def test_skill_file_exists():
    """Ensure SKILL.md exists in the expected location."""
    assert os.path.isfile(SKILL_PATH), f"SKILL.md not found at {SKILL_PATH}"

def test_skill_frontmatter_validity():
    """Ensure the YAML frontmatter is valid and contains required Hermes fields."""
    with open(SKILL_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract YAML frontmatter bounded by ---
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    assert match is not None, "SKILL.md must contain YAML frontmatter bounded by ---"

    frontmatter = yaml.safe_load(match.group(1))

    # Validate core fields based on Hermes standard
    assert "name" in frontmatter, "Missing 'name' in frontmatter"
    assert frontmatter["name"] == "context-engineering"
    assert "description" in frontmatter, "Missing 'description' in frontmatter"
    assert len(frontmatter["description"]) > 10, "Description is too short"
    
    # Validate metadata nesting
    assert "metadata" in frontmatter, "Missing 'metadata' block"
    assert "hermes" in frontmatter["metadata"], "Missing 'metadata.hermes' block"
    assert "category" in frontmatter["metadata"]["hermes"], "Missing 'metadata.hermes.category'"

def test_referenced_files_exist():
    """Ensure all scripts and reference markdowns mentioned in SKILL.md actually exist."""
    with open(SKILL_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all mentions of references/*.md and scripts/*.py
    referenced_markdowns = set(re.findall(r'(references/[a-zA-Z0-9_-]+\.md)', content))
    referenced_scripts = set(re.findall(r'(scripts/[a-zA-Z0-9_-]+\.py)', content))

    assert len(referenced_markdowns) > 0, "No references/*.md found in SKILL.md text"
    assert len(referenced_scripts) > 0, "No scripts/*.py found in SKILL.md text"

    # Verify each mentioned markdown file exists on disk
    for rel_path in referenced_markdowns:
        full_path = os.path.join(SKILL_DIR, rel_path)
        assert os.path.isfile(full_path), f"Broken link in SKILL.md: {rel_path} does not exist"

    # Verify each mentioned script exists on disk
    for rel_path in referenced_scripts:
        full_path = os.path.join(SKILL_DIR, rel_path)
        assert os.path.isfile(full_path), f"Broken link in SKILL.md: {rel_path} does not exist"