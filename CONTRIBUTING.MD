# Contributing to STTF

Thank you for your interest in contributing — STTF is an open standard, and building a shared ecosystem is the goal.

## How to Contribute

### 1. Fork the repository
Click the Fork button on GitHub.

### 2. Create a feature branch
```bash
git checkout -b feature/my-improvement
```

### 3. Follow the project style
- Python code should follow PEP8
- Tests must accompany all major changes
- Do not introduce new opcodes without discussing via issue first

### 4. Run the test suite
```bash
python tests/test_sttf.py
```

### 5. Submit a pull request
Explain:
- What you changed
- Why
- How it fits the STTF spec

PRs are reviewed openly and must pass CI.

## Accepted Contribution Types

✓ Bug fixes  
✓ Performance improvements  
✓ New tooling (visualizers, checkers, generators)  
✓ Integrations with solvers or preprocessors  
✓ Documentation improvements  
✓ Tests and example bundles  

## Not Accepted Without Discussion

✗ New transformation opcodes  
✗ Changes to the core semantics  
✗ Breaking changes to the bundle structure  

Open an issue for major proposals.

## Code of Conduct

- Be respectful
- Be constructive
- Assume good faith
- Work collaboratively
```
