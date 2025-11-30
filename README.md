
![STTF Version](https://img.shields.io/badge/STTF-v1.0-blueviolet)
![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![Dependencies](https://img.shields.io/badge/Dependencies-None-brightgreen)
![DIMACS](https://img.shields.io/badge/CNF-DIMACS%20Standard-blue)
![Reproducible](https://img.shields.io/badge/Reproducible-Yes-2ea44f)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)


# SAT Transformation Trace Format (STTF) v1.0

A universal, deterministic standard for recording SAT CNF transformations and reconstructing models.

## Overview

STTF provides a complete framework for:

- **Reproducible SAT preprocessing**: Record exact transformation steps from CNF(A) → CNF(B)
- **Model reconstruction**: Lift SAT models from simplified formulas back to original formulas
- **Transformation verification**: Replay transformations to verify correctness
- **Standardized interchange**: Universal format for SAT toolchains

## Project Structure

```
sttf/
├── src/
│   ├── sttf_core.py       # Core library (expression eval, bundle loader, model lifting)
│   ├── sttf_replay.py     # Replay engine (reconstruct simplified CNF)
│   ├── sttf_validate.py   # Validation CLI tool
│   └── sttf_generate.py   # Bundle generator (for testing/examples)
├── tests/
│   └── test_sttf.py       # Comprehensive test suite
├── examples/              # Example bundles (generated)
└── README.md
```

## Quick Start

### Installation

```bash
# No dependencies required - pure Python 3.6+
cd sttf
```

### Generate Example Bundle

```bash
python3 src/sttf_generate.py examples/demo
```

### Validate Bundle

```bash
python3 src/sttf_validate.py examples/demo_simple
python3 src/sttf_validate.py examples/demo_simple --verbose
python3 src/sttf_validate.py examples/demo_simple --replay
```

### Run Tests

```bash
python3 tests/test_sttf.py
```

## STTF Bundle Format

Every STTF bundle contains exactly 5 files:

```
bundle/
├── original.cnf       # Original CNF in DIMACS format
├── simplified.cnf     # Simplified CNF in DIMACS format
├── transform.log      # Transformation steps (A → B)
├── reconstruct.map    # Reverse mapping rules (B → A)
└── manifest.json      # Metadata and statistics
```

### Manifest Example

```json
{
  "version": "1.0",
  "generator": {
    "tool": "example-preprocessor",
    "version": "2.4.1"
  },
  "timestamp": "2025-02-07T12:15:00Z",
  "original": { "variables": 1234, "clauses": 5600 },
  "simplified": { "variables": 890, "clauses": 4002 },
  "transformation_steps": 28111
}
```

### Transform Log Format

```
<step-id> <opcode> <arguments>
```

**Canonical Opcodes:**

| Opcode | Arguments | Description |
|--------|-----------|-------------|
| `var_rename` | `old new` | Rename variable |
| `var_elim` | `v reason` | Eliminate variable |
| `var_subst` | `v = expr` | Substitute variable with expression |
| `clause_remove` | `id reason` | Remove clause |
| `clause_add` | `[lits] source` | Add clause |
| `clause_strengthen` | `id [new_lits]` | Strengthen clause |
| `unit_derive` | `lit source` | Derive unit clause |

**Example:**

```
1 var_rename 1 10
2 var_elim 5 pure_literal
3 clause_remove 3 subsumed
4 var_subst 8 = OR(1, 2)
```

### Reconstruct Map Format

```
rev_map bvar -> avar                # Variable mapping
rev_elim v = true|false             # Constant elimination
rev_elim_expr v = expr              # Expression substitution
rev_clause_add id [literals]        # Clause added during transform
```

**Example:**

```
rev_map 10 -> 1
rev_elim 5 = false
rev_elim_expr 8 = OR(1, 2)
```

### Expression Grammar

```
expr ::= lit
       | NOT(expr)
       | AND(expr, expr)
       | OR(expr, expr)
       | XOR(expr, expr)

lit ::= <integer>  # positive or negative
```

## Python API

### Loading a Bundle

```python
from sttf_core import STTFBundle

# Load bundle
bundle = STTFBundle("/path/to/bundle")

# Access metadata
print(bundle.manifest_data)
print(f"Steps: {len(bundle.transform_steps)}")
print(f"Reverse rules: {len(bundle.rev_rules)}")

# Get summary
summary = bundle.get_transform_summary()
print(summary)
```

### Model Lifting

```python
from sttf_core import STTFBundle

bundle = STTFBundle("/path/to/bundle")

# Model for simplified CNF (dict: variable -> boolean)
model_simplified = {
    1: True,
    2: False,
    3: True,
    # ...
}

# Lift to original CNF
model_original = bundle.lift_model(model_simplified)

print(f"Original model: {model_original}")
```

### Replaying Transformations

```python
from sttf_replay import STTFReplayEngine

# Create engine
engine = STTFReplayEngine(
    "bundle/original.cnf",
    "bundle/transform.log"
)

# Replay transformation
formula = engine.replay_transformation()

# Export reconstructed CNF
dimacs = formula.to_dimacs()
print(dimacs)

# Or write to file
engine.write_simplified("reconstructed.cnf")
```

### Generating Bundles

```python
from sttf_generate import STTFBundleGenerator

# Create generator
gen = STTFBundleGenerator("/output/path")

# Set original formula
gen.set_original_cnf(
    num_vars=5,
    clauses=[
        [1, 2, 3],
        [-1, 4],
        [-2, 5]
    ]
)

# Add transformations
gen.add_var_rename(1, 10)
gen.add_var_elim(5, "pure_literal")
gen.add_clause_remove(3, "subsumed")

# Write bundle
gen.write_bundle(
    generator_name="my_preprocessor",
    generator_version="1.0"
)
```

### Expression Evaluation

```python
from sttf_core import Expr

# Create expression
expr = Expr("AND(OR(1, 2), NOT(3))")

# Evaluate with model
model = {1: True, 2: False, 3: False}
result = expr.eval(model)  # True
```

## Command-Line Tools

### Validation Tool

```bash
# Basic validation
python3 src/sttf_validate.py /path/to/bundle

# Verbose output
python3 src/sttf_validate.py /path/to/bundle --verbose

# With replay verification
python3 src/sttf_validate.py /path/to/bundle --replay
```

### Bundle Generator

```bash
# Generate example bundles
python3 src/sttf_generate.py /output/directory
```

## Testing

The test suite covers:

- Expression evaluation (all operators, nested expressions)
- CNF formula operations (add/remove/rename/eliminate)
- Bundle generation and loading
- Replay engine correctness
- Model lifting accuracy
- End-to-end integration

```bash
# Run all tests
python3 tests/test_sttf.py

# Run specific test class
python3 -m unittest tests.test_sttf.TestModelLifting

# Run with verbose output
python3 tests/test_sttf.py -v
```

## Use Cases

### SAT Preprocessors

Record your preprocessing transformations for:
- Reproducibility
- Debugging
- Benchmarking
- Model reconstruction

```python
# In your preprocessor
from sttf_generate import STTFBundleGenerator

gen = STTFBundleGenerator("output/bundle")
gen.set_original_cnf(vars, clauses)

# Apply transformations and record
for step in preprocessing_steps:
    apply_transformation(step)
    gen.add_transformation(step)

gen.write_bundle("MyPreprocessor", "2.0")
```

### SAT Solvers

Lift models from preprocessed formulas:

```python
from sttf_core import STTFBundle

bundle = STTFBundle("preprocessed/bundle")

# Solve simplified CNF
model_simplified = solve_cnf(bundle.simplified)

# Reconstruct original model
model_original = bundle.lift_model(model_simplified)

# Verify against original CNF
verify_model(bundle.original, model_original)
```

### Research & Benchmarking

Standardized format for:
- Comparing preprocessing techniques
- Reproducing experimental results
- Analyzing transformation effectiveness
- Building preprocessing benchmarks

### CNF Analysis

Analyze transformation patterns:

```python
from sttf_core import STTFBundle

bundle = STTFBundle("bundle")
summary = bundle.get_transform_summary()

print(f"Variable eliminations: {summary['opcodes'].get('var_elim', 0)}")
print(f"Clause removals: {summary['opcodes'].get('clause_remove', 0)}")
print(f"Simplification ratio: {summary['simplified_vars'] / summary['original_vars']:.2%}")
```

## Compliance Requirements

A tool is **STTF-compliant** if:

1. ✓ `original.cnf + transform.log` deterministically reproduces `simplified.cnf`
2. ✓ Any SAT model for `simplified.cnf` can be lifted to a SAT model for `original.cnf`
3. ✓ All eliminated/substituted variables have reverse rules in `reconstruct.map`
4. ✓ All opcodes are from the canonical set
5. ✓ All lines follow the EBNF grammar

Use `sttf_validate.py --replay` to verify full compliance.

## Design Principles

- **Deterministic**: Same input → same output, always
- **Complete**: All transformations tracked, no information loss
- **Reversible**: Models can always be lifted back to original
- **Minimal**: Closed opcode set, simple grammar
- **Verifiable**: Replay engine confirms correctness

## Technical Specifications

- **Format Version**: 1.0
- **Grammar**: Complete EBNF specification (see document)
- **Python Version**: 3.6+
- **Dependencies**: None (pure Python)
- **File Encoding**: UTF-8
- **CNF Format**: DIMACS standard

## Examples

See the `examples/` directory for:
- `simple/` - Basic transformations (rename, eliminate)
- `complex/` - Advanced features (substitution, strengthening)

Generate fresh examples:
```bash
python3 src/sttf_generate.py examples/my_example
```

## Future Extensions

Potential future opcodes (not in v1.0):
- `var_equiv` - Equivalence classes
- `blocked_clause` - Blocked clause elimination
- `vivification` - Clause vivification
- `inprocessing` - Mark inprocessing boundaries

## Contributing

To propose extensions or report issues:
1. Ensure backward compatibility with v1.0
2. Provide reference implementation
3. Include test cases
4. Update grammar specification

## License

This specification and reference implementation are provided for standardization purposes.

## Contact

For questions about STTF or this implementation:
- Review the complete specification document
- Check the test suite for examples
- Run validation tools on your bundles

---

**STTF v1.0** - Byt-Wyze 2025
