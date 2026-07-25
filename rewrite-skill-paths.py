#!/usr/bin/env python3
"""
SKILL.md Path Rewriting Script
================================

Converts absolute home-relative paths (~/) to working-directory-relative paths (./)
in SKILL.md files to make skills portable across installations.

Usage:
    python3 rewrite-skill-paths.py <skill.md-file> [-o output-file]
    python3 rewrite-skill-paths.py --help

Examples:
    # Rewrite in-place
    python3 rewrite-skill-paths.py skills/games/SKILL.md
    
    # Write to different output
    python3 rewrite-skill-paths.py skills/games/SKILL.md -o /tmp/rewritten.md
    
    # Dry-run (show changes without writing)
    python3 rewrite-skill-paths.py skills/games/SKILL.md --dry-run

Rewrite Rules:
    ✓ ~/skillname/        → ./skillname/        (workspace directories)
    ✓ ~/skillname/file    → ./skillname/file    (workspace files)
    ✓ ~/.hidden/          → ./.hidden/          (hidden config dirs)
    
    ✗ /etc/, /var/        → (unchanged)         (system paths)
    ✗ $VAR, ${VAR}        → (unchanged)         (environment variables)
    ✗ http://, https://   → (unchanged)         (URLs)
    ✗ C:\\Windows         → (unchanged)         (Windows paths)
    ✗ ./, ../             → (unchanged)         (already relative)

Author: Hermes Agent
Date: 2026-07-25
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Tuple


def rewrite_paths(content: str) -> Tuple[str, int]:
    """
    Rewrite ~/ paths to ./ paths in SKILL.md content.
    
    Args:
        content: The SKILL.md file content as a string
        
    Returns:
        Tuple of (rewritten_content, number_of_replacements_made)
    """
    replacements = 0
    
    # Pattern 1: ~/dirname/ or ~/dirname/file (workspace paths)
    # Matches ~/ followed by alphanumeric start, then alphanumeric/dash/underscore/slash
    # Stops at whitespace, quotes, backticks, or end of path segment
    pattern1 = r'~/([a-zA-Z][a-zA-Z0-9_-]*(?:/[a-zA-Z0-9_./-]*)?)'
    
    def repl1(match):
        nonlocal replacements
        replacements += 1
        return f'./{match.group(1)}'
    
    content = re.sub(pattern1, repl1, content)
    
    # Pattern 2: ~/.hidden/ (hidden config directories like ~/.austin/, ~/.ssh/)
    # Matches ~/ followed by dot, then alphanumeric start
    pattern2 = r'~/\.([a-zA-Z][a-zA-Z0-9_.-]*(?:/[a-zA-Z0-9_./-]*)?)'
    
    def repl2(match):
        nonlocal replacements
        replacements += 1
        return f'./.{match.group(1)}'
    
    content = re.sub(pattern2, repl2, content)
    
    return content, replacements


def process_file(input_path: Path, output_path: Path | None = None, dry_run: bool = False) -> bool:
    """
    Process a single SKILL.md file.
    
    Args:
        input_path: Path to the input SKILL.md file
        output_path: Path to write output (None = overwrite input)
        dry_run: If True, show changes but don't write
        
    Returns:
        True if successful, False otherwise
    """
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        return False
    
    if not input_path.is_file():
        print(f"Error: Not a file: {input_path}", file=sys.stderr)
        return False
    
    try:
        # Read input file
        content = input_path.read_text(encoding='utf-8')
        
        # Rewrite paths
        new_content, count = rewrite_paths(content)
        
        # Report results
        if dry_run:
            print(f"[DRY-RUN] {input_path}: {count} path(s) would be rewritten")
            if count > 0:
                # Show a preview of changes
                print("\n--- Preview of changes ---")
                # Show first few differences
                old_lines = content.splitlines(keepends=True)
                new_lines = new_content.splitlines(keepends=True)
                shown = 0
                for i, (old, new) in enumerate(zip(old_lines, new_lines), 1):
                    if old != new and shown < 10:
                        print(f"Line {i}:")
                        print(f"  - {old.rstrip()}")
                        print(f"  + {new.rstrip()}")
                        shown += 1
                if count > 10:
                    print(f"  ... and {count - 10} more changes")
                print("--- End preview ---\n")
        else:
            # Determine output destination
            target = output_path if output_path is not None else input_path
            
            # Write output
            target.write_text(new_content, encoding='utf-8')
            print(f"✓ {input_path}: {count} path(s) rewritten → {target}")
        
        return True
        
    except Exception as e:
        print(f"Error processing {input_path}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Rewrite ~/ paths to ./ in SKILL.md files for portability",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s skills/games/SKILL.md              # Rewrite in-place
  %(prog)s skills/games/SKILL.md -o out.md    # Write to different file
  %(prog)s skills/games/SKILL.md --dry-run    # Preview changes only
        """
    )
    
    parser.add_argument(
        'input',
        type=Path,
        help="Input SKILL.md file path"
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help="Output file path (default: overwrite input)",
        metavar='FILE'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be changed without writing"
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not args.input.exists():
        print(f"Error: Input file does not exist: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Validate output directory if specified
    if args.output:
        output_dir = args.output.parent
        if not output_dir.exists():
            print(f"Error: Output directory does not exist: {output_dir}", file=sys.stderr)
            sys.exit(1)
    
    # Process the file
    success = process_file(args.input, args.output, args.dry_run)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
