#!/usr/bin/env python3
"""
STTF Setup and Demo
Sets up the STTF project and runs a complete demonstration.
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from sttf_generate import generate_simple_example, generate_complex_example
from sttf_core import STTFBundle
from sttf_replay import replay_bundle


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def demo_simple_bundle():
    """Demonstrate simple STTF bundle."""
    print_header("DEMO: Simple STTF Bundle")
    
    # Generate bundle
    bundle_path = "/tmp/sttf_demo_simple"
    print(f"\n1. Generating simple bundle at {bundle_path}")
    generate_simple_example(bundle_path)
    
    # Load and inspect
    print("\n2. Loading and inspecting bundle...")
    bundle = STTFBundle(bundle_path)
    
    print(f"\n   Manifest:")
    print(f"   - Generator: {bundle.manifest_data['generator']['tool']}")
    print(f"   - Original: {bundle.manifest_data['original']['variables']} vars, "
          f"{bundle.manifest_data['original']['clauses']} clauses")
    print(f"   - Simplified: {bundle.manifest_data['simplified']['variables']} vars, "
          f"{bundle.manifest_data['simplified']['clauses']} clauses")
    
    print(f"\n   Transformations:")
    for i, (step, opcode, args) in enumerate(bundle.transform_steps[:5]):
        print(f"   {step}. {opcode} {args}")
    if len(bundle.transform_steps) > 5:
        print(f"   ... and {len(bundle.transform_steps) - 5} more")
    
    print(f"\n   Reverse rules:")
    for rule in bundle.rev_rules[:5]:
        print(f"   - {rule[0]}: {rule[1:]}")
    if len(bundle.rev_rules) > 5:
        print(f"   ... and {len(bundle.rev_rules) - 5} more")
    
    # Replay transformation
    print("\n3. Replaying transformation...")
    formula = replay_bundle(bundle_path)
    print(f"   ✓ Replay successful")
    print(f"   ✓ Simplified formula has {len(formula.clauses)} clauses")
    
    # Model lifting demo
    print("\n4. Demonstrating model lifting...")
    # Create a sample model for simplified CNF
    model_simplified = {1: True, 2: False, 5: True}
    print(f"   Model for simplified CNF: {model_simplified}")
    
    model_original = bundle.lift_model(model_simplified)
    print(f"   Model for original CNF: {model_original}")
    print(f"   ✓ Model lifted successfully")
    
    return True


def demo_complex_bundle():
    """Demonstrate complex STTF bundle with substitutions."""
    print_header("DEMO: Complex STTF Bundle with Substitutions")
    
    # Generate bundle
    bundle_path = "/tmp/sttf_demo_complex"
    print(f"\n1. Generating complex bundle at {bundle_path}")
    generate_complex_example(bundle_path)
    
    # Load and get summary
    print("\n2. Loading bundle and generating summary...")
    bundle = STTFBundle(bundle_path)
    summary = bundle.get_transform_summary()
    
    print(f"\n   Summary Statistics:")
    print(f"   - Total transformation steps: {summary['total_steps']}")
    print(f"   - Variable reduction: {summary['original_vars']} → {summary['simplified_vars']}")
    print(f"   - Clause reduction: {summary['original_clauses']} → {summary['simplified_clauses']}")
    
    print(f"\n   Opcode breakdown:")
    for opcode, count in sorted(summary['opcodes'].items()):
        print(f"   - {opcode}: {count}")
    
    # Test replay
    print("\n3. Testing replay engine...")
    formula = replay_bundle(bundle_path)
    print(f"   ✓ Replay successful")
    print(f"   ✓ Active variables: {sorted(formula.get_active_vars())}")
    
    return True


def demo_expression_evaluation():
    """Demonstrate boolean expression evaluation."""
    print_header("DEMO: Boolean Expression Evaluation")
    
    from sttf_core import Expr
    
    expressions = [
        ("Simple literal", "5", {5: True}),
        ("Negated literal", "-3", {3: False}),
        ("NOT operator", "NOT(2)", {2: False}),
        ("AND operator", "AND(1, 2)", {1: True, 2: True}),
        ("OR operator", "OR(1, 2)", {1: False, 2: True}),
        ("XOR operator", "XOR(1, 2)", {1: True, 2: False}),
        ("Nested expression", "AND(OR(1, 2), NOT(3))", {1: True, 2: False, 3: False}),
        ("Complex expression", "OR(AND(1, 2), XOR(3, 4))", {1: True, 2: True, 3: False, 4: True})
    ]
    
    print("\nEvaluating expressions:")
    for name, expr_str, model in expressions:
        expr = Expr(expr_str)
        result = expr.eval(model)
        print(f"\n   {name}:")
        print(f"   Expression: {expr_str}")
        print(f"   Model: {model}")
        print(f"   Result: {result}")
    
    return True


def run_tests():
    """Run the test suite."""
    print_header("Running Test Suite")
    
    import subprocess
    result = subprocess.run(
        [sys.executable, str(project_root / "tests" / "test_sttf.py")],
        cwd=str(project_root)
    )
    
    return result.returncode == 0


def main():
    """Run complete demo."""
    print_header("STTF v1.0 - Complete Demonstration")
    print("\nSAT Transformation Trace Format")
    print("Deterministic APIs for Hard Problems")
    
    try:
        # Run demos
        if not demo_simple_bundle():
            return 1
        
        if not demo_complex_bundle():
            return 1
        
        if not demo_expression_evaluation():
            return 1
        
        # Run tests
        if not run_tests():
            print("\n✗ Some tests failed")
            return 1
        
        # Final summary
        print_header("Demo Complete - All Systems Operational")
        print("\n✓ Simple bundle generation and validation")
        print("✓ Complex bundle with substitutions")
        print("✓ Expression evaluation")
        print("✓ Model lifting")
        print("✓ Replay engine")
        print("✓ All tests passed")
        
        print("\nNext steps:")
        print("  - Review README.md for detailed documentation")
        print("  - Check examples/ directory for generated bundles")
        print("  - Run 'python3 src/sttf_validate.py --help' for CLI usage")
        print("  - Explore Python API in src/sttf_core.py")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
