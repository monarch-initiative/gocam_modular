# Makefile for gocam_modular translator ingest operations
#
# This Makefile provides convenient targets for running the translator ingest
# functionality, including cloning the translator-ingests repository and
# executing the go_cam source processing.

.PHONY: help ingest ingest-clean test clean

# Default target
help:
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  ingest       - Run the translator ingest for go_cam sources"
	@echo "  ingest-clean - Clean up any temporary directories and run ingest"
	@echo "  test         - Run all tests"
	@echo "  clean        - Clean up temporary files and directories"

# Run the translator ingest and generate TSV files
ingest:
	@echo "Running translator ingest for go_cam sources..."
	@uv run python -c "import sys; sys.path.insert(0, 'src'); from gocam_modular.translator_ingest import checkout_and_run_translator_ingests; from pathlib import Path; import shutil; repo_path, result = checkout_and_run_translator_ingests(); output_dir = Path('output'); output_dir.mkdir(exist_ok=True); go_cam_dir = repo_path / 'data' / 'go_cam'; [shutil.copy2(f, output_dir / f.name) for f in go_cam_dir.iterdir() if f.is_file()]; print(f'Files copied from: {go_cam_dir}')"
	@echo "Converting JSONL files to TSV format..."
	@uv run python scripts/convert_to_tsv.py
	@echo "Ingest completed successfully!"

# Clean up and run ingest
ingest-clean: clean ingest

# Run tests
test:
	@echo "Running tests..."
	uv run pytest tests/test_translator_ingest.py -v
	@echo "Running doctests..."
	uv run python -m doctest src/gocam_modular/translator_ingest.py

# Clean up temporary files
clean:
	@echo "Cleaning up temporary files..."
	@find /tmp -name "translator-ingests*" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete."

# Advanced target: run ingest with custom repository URL
ingest-custom:
	@echo "Running translator ingest with custom repository..."
	@read -p "Enter repository URL: " repo_url; \
	uv run python -c "from gocam_modular.translator_ingest import checkout_and_run_translator_ingests; repo_path, result = checkout_and_run_translator_ingests(repo_url='$$repo_url'); print(f'Repository cloned to: {repo_path}'); print(f'Make output:\\n{result.stdout}')"

# Target to just clone the repository without running make
clone-only:
	@echo "Cloning translator-ingests repository only..."
	uv run python -c "from gocam_modular.translator_ingest import clone_translator_ingests; repo_path = clone_translator_ingests(); print(f'Repository cloned to: {repo_path}')"