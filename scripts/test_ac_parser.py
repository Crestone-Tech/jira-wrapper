#!/usr/bin/env python3
"""Test script for AC parser - generates preview table."""

import sys
import argparse
from pathlib import Path

# Add parent directory to path to import jira_wrapper
sys.path.insert(0, str(Path(__file__).parent.parent))

from jira_wrapper.ac_parser import parse_and_preview


def main():
    """Run parser on test file and output preview."""
    parser = argparse.ArgumentParser(description="Parse acceptance criteria and generate preview table")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).parent.parent / "tests" / "orchestrator_acceptance_criteria.md",
        help="Input markdown file with acceptance criteria"
    )
    parser.add_argument(
        "--project",
        default="PROJ",
        help="Jira project key (for preview purposes)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (if not specified, prints to stdout)"
    )
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    print(f"Parsing: {args.input}")
    print("=" * 80)
    print()
    
    preview = parse_and_preview(args.input, project_key=args.project)
    
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(preview, encoding='utf-8')
        print(f"Preview saved to: {args.output}")
    else:
        print(preview)


if __name__ == "__main__":
    main()

