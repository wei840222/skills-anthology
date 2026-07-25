#!/usr/bin/env python3
"""Test edge cases for path rewriting"""
import sys
import importlib.util

spec = importlib.util.spec_from_file_location("rewrite_skill_paths", "/home/wei/Documents/Gitea/wei840222/skills/.worktrees/t_fb22bf05/rewrite-skill-paths.py")
rewrite_skill_paths = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rewrite_skill_paths)
rewrite_paths = rewrite_skill_paths.rewrite_paths

test_cases = [
    # (input, expected_output, description)
    ("~/games/", "./games/", "Basic workspace directory"),
    ("~/writing/memory.md", "./writing/memory.md", "Workspace file path"),
    ("~/.config/", "./.config/", "Hidden config directory"),
    ("~/.ssh/config", "./.ssh/config", "Hidden config file"),
    ("/etc/passwd", "/etc/passwd", "System path unchanged"),
    ("$HOME/.config", "$HOME/.config", "Env var unchanged"),
    ("${HOME}/test", "${HOME}/test", "Env var with braces unchanged"),
    ("https://example.com/path", "https://example.com/path", "URL unchanged"),
    ("http://localhost:8080", "http://localhost:8080", "HTTP URL unchanged"),
    ("C:\\Users\\test", "C:\\Users\\test", "Windows path unchanged"),
    ("./relative/path", "./relative/path", "Already relative unchanged"),
    ("../parent/path", "../parent/path", "Parent relative unchanged"),
    ("~/my-project/", "./my-project/", "Hyphenated directory"),
    ("~/my_project/", "./my_project/", "Underscored directory"),
    ("~/Project123/", "./Project123/", "Alphanumeric directory"),
    ("Multiple: ~/a/ and ~/b/", "Multiple: ./a/ and ./b/", "Multiple paths in one line"),
    ("Mixed: ~/games/ and /etc/ and $HOME", "Mixed: ./games/ and /etc/ and $HOME", "Mixed path types"),
]

print("=== Edge Case Tests ===\n")
passed = 0
failed = 0

for input_text, expected, description in test_cases:
    result, count = rewrite_paths(input_text)
    if result == expected:
        print(f"✓ {description}")
        passed += 1
    else:
        print(f"✗ {description}")
        print(f"  Input:    {input_text}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        failed += 1

print(f"\n{passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
