import sys
sys.path.insert(0, 'src')

from sttf_core import STTFBundle, Expr
from sttf_replay import replay_bundle

print("=" * 60)
print("STTF Python API Test")
print("=" * 60)

# 1. Load a bundle
print("\n1. Loading bundle...")
bundle = STTFBundle('examples/demo_simple')
print("   ✓ Bundle loaded successfully")

# 2. Get summary
print("\n2. Bundle summary:")
summary = bundle.get_transform_summary()
print(f"   Original: {summary['original_vars']} vars, {summary['original_clauses']} clauses")
print(f"   Simplified: {summary['simplified_vars']} vars, {summary['simplified_clauses']} clauses")
print(f"   Transform steps: {summary['total_steps']}")
print(f"   Opcodes used: {summary['opcodes']}")

# 3. Replay transformation
print("\n3. Replaying transformation...")
formula = replay_bundle('examples/demo_simple')
print(f"   ✓ Replay successful")
print(f"   Resulting clauses: {len(formula.clauses)}")
print(f"   Active variables: {sorted(formula.get_active_vars())}")

# 4. Model lifting
print("\n4. Model lifting example:")
model_B = {1: True, 2: False, 5: True}
print(f"   Model for simplified CNF: {model_B}")
model_A = bundle.lift_model(model_B)
print(f"   Model for original CNF:   {model_A}")
print("   ✓ Model lifted successfully")

# 5. Expression evaluation
print("\n5. Expression evaluation:")
expr = Expr("AND(OR(1, 2), NOT(3))")
model = {1: True, 2: False, 3: False}
result = expr.eval(model)
print(f"   Expression: AND(OR(1, 2), NOT(3))")
print(f"   Model: {model}")
print(f"   Result: {result}")

print("\n" + "=" * 60)
print("All API tests passed! ✓")
print("=" * 60)