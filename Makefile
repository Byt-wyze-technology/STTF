.PHONY: help demo test validate clean examples all

help:
	@echo "STTF v1.0 - Makefile Commands"
	@echo ""
	@echo "  make demo       - Run complete demonstration"
	@echo "  make test       - Run test suite"
	@echo "  make examples   - Generate example bundles"
	@echo "  make validate   - Validate example bundles"
	@echo "  make clean      - Remove generated files"
	@echo "  make all        - Run everything (demo + test + examples)"
	@echo ""

demo:
	@echo "Running STTF demonstration..."
	python3 demo.py

test:
	@echo "Running test suite..."
	python3 tests/test_sttf.py

examples:
	@echo "Generating example bundles..."
	@mkdir -p examples
	python3 src/sttf_generate.py examples/demo

validate: examples
	@echo "Validating simple example..."
	python3 src/sttf_validate.py examples/demo_simple --verbose
	@echo ""
	@echo "Validating complex example..."
	python3 src/sttf_validate.py examples/demo_complex --verbose

clean:
	@echo "Cleaning generated files..."
	rm -rf examples/demo_* /tmp/sttf_*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete"

all: demo test examples validate
	@echo ""
	@echo "All tasks complete!"
