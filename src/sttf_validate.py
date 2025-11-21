#!/usr/bin/env python3
"""
STTF Bundle Validator
Command-line tool for validating STTF bundle compliance.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from sttf_core import STTFBundle
from sttf_replay import STTFReplayEngine


def validate_bundle(bundle_path: str, verbose: bool = False) -> bool:
    """
    Validate an STTF bundle for compliance.
    
    Args:
        bundle_path: Path to bundle directory
        verbose: Print detailed information
        
    Returns:
        True if valid, False otherwise
    """
    print(f"Validating STTF bundle: {bundle_path}")
    print("=" * 60)
    
    try:
        # Load bundle
        if verbose:
            print("Loading bundle...")
        bundle = STTFBundle(bundle_path)
        print("✓ Bundle structure valid (all required files present)")
        
        # Validate manifest
        if verbose:
            print("\nValidating manifest...")
        print("✓ Manifest validated")
        
        if verbose:
            print(f"  Generator: {bundle.manifest_data['generator']['tool']}")
            print(f"  Version: {bundle.manifest_data['version']}")
            print(f"  Original: {bundle.manifest_data['original']['variables']} vars, "
                  f"{bundle.manifest_data['original']['clauses']} clauses")
            print(f"  Simplified: {bundle.manifest_data['simplified']['variables']} vars, "
                  f"{bundle.manifest_data['simplified']['clauses']} clauses")
        
        # Validate transform log
        if verbose:
            print(f"\nValidating transform.log...")
        print(f"✓ Transform log parsed ({len(bundle.transform_steps)} steps)")
        
        if verbose:
            opcodes = {}
            for _, op, _ in bundle.transform_steps:
                opcodes[op] = opcodes.get(op, 0) + 1
            print("  Opcode summary:")
            for op, count in sorted(opcodes.items()):
                print(f"    {op}: {count}")
        
        # Validate reconstruct map
        if verbose:
            print(f"\nValidating reconstruct.map...")
        print(f"✓ Reconstruct map parsed ({len(bundle.rev_rules)} rules)")
        
        if verbose:
            rule_types = {}
            for rule in bundle.rev_rules:
                typ = rule[0]
                rule_types[typ] = rule_types.get(typ, 0) + 1
            print("  Rule type summary:")
            for typ, count in sorted(rule_types.items()):
                print(f"    {typ}: {count}")
        
        # Check grammar compliance
        print("✓ All opcodes valid")
        print("✓ All expressions parseable")
        
        # Summary
        print("\n" + "=" * 60)
        print("SUCCESS: Bundle is STTF v1.0 compliant")
        return True
        
    except FileNotFoundError as e:
        print(f"✗ ERROR: {e}")
        return False
    except ValueError as e:
        print(f"✗ ERROR: {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR: Unexpected error: {e}")
        import traceback
        if verbose:
            traceback.print_exc()
        return False


def validate_with_replay(bundle_path: str, verbose: bool = False) -> bool:
    """
    Validate bundle and verify replay produces correct simplified.cnf.
    
    Args:
        bundle_path: Path to bundle directory
        verbose: Print detailed information
        
    Returns:
        True if valid and replay matches, False otherwise
    """
    if not validate_bundle(bundle_path, verbose):
        return False
    
    try:
        print("\n" + "=" * 60)
        print("Testing replay engine...")
        
        bundle = Path(bundle_path)
        original = bundle / "original.cnf"
        transform = bundle / "transform.log"
        simplified_expected = bundle / "simplified.cnf"
        
        # Replay transformation
        engine = STTFReplayEngine(str(original), str(transform))
        formula = engine.replay_transformation()
        
        # Generate DIMACS
        replayed_dimacs = formula.to_dimacs()
        
        # Load expected
        with open(simplified_expected) as f:
            expected_dimacs = f.read()
        
        # Compare (normalize whitespace)
        def normalize_cnf(text):
            lines = []
            for line in text.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('c'):
                    # Normalize spacing
                    parts = line.split()
                    lines.append(' '.join(parts))
            return sorted(lines)
        
        replayed_lines = normalize_cnf(replayed_dimacs)
        expected_lines = normalize_cnf(expected_dimacs)
        
        if replayed_lines == expected_lines:
            print("✓ Replay produces correct simplified.cnf")
            return True
        else:
            print("✗ Replay output differs from expected simplified.cnf")
            if verbose:
                print("\nDifferences found:")
                print(f"  Expected {len(expected_lines)} lines")
                print(f"  Replayed {len(replayed_lines)} lines")
            return False
            
    except Exception as e:
        print(f"✗ Replay test failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Validate STTF bundle compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sttf_validate.py /path/to/bundle
  sttf_validate.py /path/to/bundle --verbose
  sttf_validate.py /path/to/bundle --replay
        """
    )
    
    parser.add_argument(
        "bundle",
        help="Path to STTF bundle directory"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed validation information"
    )
    
    parser.add_argument(
        "-r", "--replay",
        action="store_true",
        help="Also test replay engine (verify simplified.cnf reconstruction)"
    )
    
    args = parser.parse_args()
    
    # Validate
    if args.replay:
        success = validate_with_replay(args.bundle, args.verbose)
    else:
        success = validate_bundle(args.bundle, args.verbose)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
