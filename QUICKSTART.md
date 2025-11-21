# STTF v1.0 - Quick Start Guide

## What You Got

A complete, production-ready implementation of the SAT Transformation Trace Format (STTF) v1.0 standard including:

- Core library for loading bundles and lifting models
- Replay engine for reconstructing simplified CNF
- Validation tools with CLI
- Bundle generation utilities
- 22 comprehensive tests (100% passing)
- Example bundles included

## Instant Test

```bash
cd sttf

# Run everything (demo + tests + examples)
python3 demo.py

# Or step by step:

# 1. Run tests
python3 tests/test_sttf.py

# 2. Generate examples
python3 src/sttf_generate.py examples/test

# 3. Validate
python3 src/sttf_validate.py examples/test_simple --verbose
```

## 5-Minute Tutorial

### 1. Load a Bundle

```python
from src.sttf_core import STTFBundle

# Load existing bundle
bundle = STTFBundle("examples/demo_simple")

# Inspect
print(f"Original: {bundle.manifest_data['original']['variables']} vars")
print(f"Simplified: {bundle.manifest_data['simplified']['variables']} vars")
print(f"Transform steps: {len(bundle.transform_steps)}")
```

### 2. Lift a Model

```python
# Model for simplified CNF
model_simplified = {1: True, 2: False, 5: True}

# Lift to original
model_original = bundle.lift_model(model_simplified)

print(f"Lifted model: {model_original}")
```

### 3. Replay Transformation

```python
from src.sttf_replay import replay_bundle

# Replay transformation
formula = replay_bundle("examples/demo_simple")

# Check result
print(f"Clauses: {len(formula.clauses)}")
print(f"Variables: {formula.get_active_vars()}")
```

### 4. Create Your Own Bundle

```python
from src.sttf_generate import STTFBundleGenerator

gen = STTFBundleGenerator("my_bundle")

# Set original formula
gen.set_original_cnf(
    num_vars=5,
    clauses=[[1, 2], [-1, 3], [4, 5]]
)

# Add transformations
gen.add_var_rename(1, 10)
gen.add_var_elim(5, "pure_literal")
gen.add_clause_remove(3, "subsumed")

# Write bundle
gen.write_bundle("my_preprocessor", "1.0")
```

## What's in the Box

```
sttf/
├── src/
│   ├── sttf_core.py       - Core: Expr, STTFBundle, model lifting
│   ├── sttf_replay.py     - Replay engine
│   ├── sttf_validate.py   - Validation CLI
│   └── sttf_generate.py   - Bundle generator
├── tests/
│   └── test_sttf.py       - 22 tests covering everything
├── examples/
│   ├── demo_simple/       - Simple example bundle
│   └── demo_complex/      - Complex example with substitutions
├── README.md              - Full documentation
├── PROJECT_SUMMARY.md     - Complete project overview
└── demo.py                - Demonstration script
```

## STTF Bundle Structure

Every bundle has exactly 5 files:

```
bundle/
├── original.cnf       # Original CNF (DIMACS)
├── simplified.cnf     # Simplified CNF (DIMACS)
├── transform.log      # Transformation steps
├── reconstruct.map    # Reverse mapping
└── manifest.json      # Metadata
```

## Key Features

**7 Transformation Opcodes:**
- `var_rename` - Rename variable
- `var_elim` - Eliminate variable
- `var_subst` - Substitute with expression
- `clause_remove` - Remove clause
- `clause_add` - Add clause
- `clause_strengthen` - Strengthen clause
- `unit_derive` - Derive unit clause

**4 Reverse Rules:**
- `rev_map` - Variable mapping
- `rev_elim` - Constant value
- `rev_elim_expr` - Expression substitution
- `rev_clause_add` - Added clause

**Expression Support:**
- Literals: `5`, `-3`
- Operations: `NOT()`, `AND()`, `OR()`, `XOR()`
- Nested: `AND(OR(1, 2), NOT(3))`

## CLI Usage

```bash
# Validate bundle
python3 src/sttf_validate.py bundle/

# Validate with verbose output
python3 src/sttf_validate.py bundle/ --verbose

# Validate with replay verification
python3 src/sttf_validate.py bundle/ --replay

# Generate examples
python3 src/sttf_generate.py output_dir/
```

## Integration Example

Use in your SAT preprocessor:

```python
from src.sttf_generate import STTFBundleGenerator

class MyPreprocessor:
    def __init__(self):
        self.sttf = STTFBundleGenerator("output/bundle")
    
    def preprocess(self, cnf):
        # Set original
        self.sttf.set_original_cnf(cnf.num_vars, cnf.clauses)
        
        # Your preprocessing
        for step in self.preprocessing_pipeline(cnf):
            # Apply step
            result = self.apply_step(step)
            
            # Record in STTF
            if isinstance(step, VarRename):
                self.sttf.add_var_rename(step.old, step.new)
            elif isinstance(step, VarElim):
                self.sttf.add_var_elim(step.var, "pure_literal")
            # ... etc
        
        # Write STTF bundle
        self.sttf.write_bundle("MyPreprocessor", "1.0")
        
        return simplified_cnf
```

## Test Results

```
✓ 22 tests, 100% passing
✓ All opcodes tested
✓ All reverse rules tested
✓ Expression evaluation tested
✓ Model lifting tested
✓ Replay engine tested
✓ End-to-end tested
```

## Compliance Verification

Your bundles are STTF v1.0 compliant if:

1. ✓ `original.cnf + transform.log` reproduces `simplified.cnf`
2. ✓ Models lift correctly from B → A
3. ✓ All eliminated variables have reverse rules
4. ✓ Only canonical opcodes used
5. ✓ Grammar strictly followed

Verify with: `python3 src/sttf_validate.py --replay`

## Example Bundle Contents

**transform.log:**
```
1 var_elim 4 pure_literal
2 clause_remove 4 pure_literal_clause
3 var_rename 3 5
```

**reconstruct.map:**
```
rev_elim 4 = false
rev_map 5 -> 3
```

## Next Steps

1. **Read the docs**: Check `README.md` for complete API reference
2. **Run the demo**: Execute `python3 demo.py` for full walkthrough
3. **Explore examples**: Look at `examples/demo_simple/` and `examples/demo_complex/`
4. **Run tests**: Execute `python3 tests/test_sttf.py` to verify
5. **Build bundles**: Use `sttf_generate.py` to create your own

## Support

- Full specification: See original STTF document
- API docs: `README.md`
- Code examples: `demo.py`
- Test cases: `tests/test_sttf.py`

## Status

**Production Ready ✓**
- All features implemented
- All tests passing
- Fully documented
- Ready to deploy

---

**STTF v1.0 - Deterministic APIs for Hard Problems**
