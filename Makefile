.PHONY: help test test-report install clean

help:
	@echo "LLM Hub - Development Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  install        Install packages in editable mode"
	@echo "  test           Run tests with pytest"
	@echo "  test-report    Run tests and generate TER report"
	@echo "  clean          Clean build artifacts and cache"
	@echo ""

install:
	pip install -e packages/llmhub_runtime
	pip install -e packages/llmhub

test:
	pytest packages/ -v

test-report:
	python -m llmhub.tools.run_tests_with_report

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
