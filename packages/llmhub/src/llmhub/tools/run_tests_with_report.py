#!/usr/bin/env python3
"""
Test Execution Report (TER) runner.

Executes pytest test suite and generates structured JSON/Markdown reports.

Usage:
    python -m llmhub.tools.run_tests_with_report

Reports are saved to: reports/test-execution/
Format: TER-YYYYMMDD-HHMM-<short_sha>.json (and optional .md)
"""
import sys
import json
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from typing import Optional, Any
import xml.etree.ElementTree as ET


def get_git_info() -> dict[str, str]:
    """Get current git commit and branch."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        short_sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        return {
            "commit": commit,
            "short_sha": short_sha,
            "branch": branch
        }
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {
            "commit": "unknown",
            "short_sha": "unknown",
            "branch": "unknown"
        }


def get_llmhub_version() -> str:
    """Get llmhub version from pyproject.toml."""
    try:
        import tomli
        pyproject_path = Path(__file__).parent.parent.parent.parent.parent / "pyproject.toml"
        
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomli.load(f)
                return data.get("project", {}).get("version", "unknown")
    except:
        pass
    
    # Fallback: try to import and get version
    try:
        from importlib.metadata import version
        return version("llmhub")
    except:
        return "unknown"


def run_pytest_with_xml(workspace_root: Path) -> tuple[int, Path]:
    """
    Run pytest and generate JUnit XML output.
    
    Returns:
        (exit_code, xml_path)
    """
    # Create temp directory for JUnit XML
    reports_dir = workspace_root / "reports" / "test-execution"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    xml_path = reports_dir / "pytest-results.xml"
    
    # Run pytest with JUnit XML output
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(workspace_root / "packages"),
        "--junitxml",
        str(xml_path),
        "-v",
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode, xml_path


def parse_junit_xml(xml_path: Path) -> dict[str, Any]:
    """
    Parse JUnit XML into TER format.
    
    Returns:
        Dict with suites, summary, etc.
    """
    if not xml_path.exists():
        return {
            "suites": [],
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0,
                "duration_seconds": 0.0,
                "status": "error"
            }
        }
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Parse test suites
    suites = []
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    total_errors = 0
    total_duration = 0.0
    
    # Handle both <testsuites> and <testsuite> root elements
    testsuite_elements = []
    if root.tag == "testsuites":
        testsuite_elements = root.findall("testsuite")
    elif root.tag == "testsuite":
        testsuite_elements = [root]
    
    for testsuite in testsuite_elements:
        suite_name = testsuite.get("name", "unknown")
        suite_tests = int(testsuite.get("tests", "0"))
        suite_failures = int(testsuite.get("failures", "0"))
        suite_errors = int(testsuite.get("errors", "0"))
        suite_skipped = int(testsuite.get("skipped", "0"))
        suite_time = float(testsuite.get("time", "0.0"))
        
        # Parse individual test cases
        tests = []
        for testcase in testsuite.findall("testcase"):
            test_name = testcase.get("name", "unknown")
            test_classname = testcase.get("classname", "")
            test_time = float(testcase.get("time", "0.0"))
            
            # Determine status
            status = "passed"
            error_info = None
            
            failure = testcase.find("failure")
            error = testcase.find("error")
            skipped = testcase.find("skipped")
            
            if failure is not None:
                status = "failed"
                error_info = {
                    "type": failure.get("type", "AssertionError"),
                    "message": failure.get("message", ""),
                    "traceback": failure.text or ""
                }
            elif error is not None:
                status = "error"
                error_info = {
                    "type": error.get("type", "Error"),
                    "message": error.get("message", ""),
                    "traceback": error.text or ""
                }
            elif skipped is not None:
                status = "skipped"
                error_info = {
                    "reason": skipped.get("message", "")
                }
            
            test_id = f"{test_classname}::{test_name}" if test_classname else test_name
            
            tests.append({
                "id": test_id,
                "name": test_name,
                "classname": test_classname,
                "status": status,
                "duration_seconds": test_time,
                "tags": [],  # pytest doesn't include tags in JUnit XML by default
                "error": error_info
            })
        
        suite_passed = suite_tests - suite_failures - suite_errors - suite_skipped
        
        suites.append({
            "name": suite_name,
            "path": testsuite.get("file", ""),
            "summary": {
                "total": suite_tests,
                "passed": suite_passed,
                "failed": suite_failures,
                "skipped": suite_skipped,
                "errors": suite_errors,
                "duration_seconds": suite_time
            },
            "tests": tests
        })
        
        total_tests += suite_tests
        total_passed += suite_passed
        total_failed += suite_failures
        total_skipped += suite_skipped
        total_errors += suite_errors
        total_duration += suite_time
    
    # Determine overall status
    if total_failed > 0 or total_errors > 0:
        status = "failed"
    elif total_tests == 0:
        status = "error"
    else:
        status = "passed"
    
    return {
        "suites": suites,
        "summary": {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "skipped": total_skipped,
            "errors": total_errors,
            "duration_seconds": round(total_duration, 3),
            "status": status
        }
    }


def generate_markdown_report(ter_data: dict[str, Any]) -> str:
    """Generate Markdown summary from TER JSON."""
    md = []
    
    # Header
    md.append(f"# Test Execution Report")
    md.append(f"")
    md.append(f"**Run ID**: `{ter_data['run_id']}`  ")
    md.append(f"**Timestamp**: {ter_data['timestamp']}  ")
    md.append(f"**Commit**: `{ter_data['commit'][:12]}` ({ter_data['branch']})  ")
    md.append(f"**Status**: **{ter_data['summary']['status'].upper()}**  ")
    md.append(f"")
    
    # Environment
    md.append(f"## Environment")
    md.append(f"")
    md.append(f"- **Python**: {ter_data['environment']['python_version']}")
    md.append(f"- **OS**: {ter_data['environment']['os']}")
    md.append(f"- **LLMHub**: {ter_data['environment']['llmhub_version']}")
    md.append(f"")
    
    # Summary
    summary = ter_data['summary']
    md.append(f"## Summary")
    md.append(f"")
    md.append(f"| Metric | Value |")
    md.append(f"|--------|-------|")
    md.append(f"| Total Tests | {summary['total_tests']} |")
    md.append(f"| Passed | {summary['passed']} ✓ |")
    md.append(f"| Failed | {summary['failed']} ✗ |")
    md.append(f"| Skipped | {summary['skipped']} ⊘ |")
    md.append(f"| Errors | {summary['errors']} ⚠ |")
    md.append(f"| Duration | {summary['duration_seconds']}s |")
    md.append(f"")
    
    # Suites
    md.append(f"## Test Suites")
    md.append(f"")
    
    for suite in ter_data['suites']:
        suite_summary = suite['summary']
        status_icon = "✓" if suite_summary['failed'] == 0 and suite_summary['errors'] == 0 else "✗"
        
        md.append(f"### {status_icon} {suite['name']}")
        md.append(f"")
        md.append(f"**Path**: `{suite['path']}`  ")
        md.append(f"**Total**: {suite_summary['total']} | **Passed**: {suite_summary['passed']} | **Failed**: {suite_summary['failed']} | **Skipped**: {suite_summary['skipped']}  ")
        md.append(f"**Duration**: {suite_summary['duration_seconds']}s  ")
        md.append(f"")
        
        # Show failed tests if any
        failed_tests = [t for t in suite['tests'] if t['status'] in ['failed', 'error']]
        if failed_tests:
            md.append(f"#### Failed Tests")
            md.append(f"")
            for test in failed_tests:
                md.append(f"- **{test['name']}** ({test['status']})")
                if test.get('error'):
                    md.append(f"  - {test['error'].get('message', '')}")
            md.append(f"")
    
    return "\n".join(md)


def main():
    """Main entry point."""
    workspace_root = Path(__file__).parent.parent.parent.parent.parent.parent
    
    # Get git info
    git_info = get_git_info()
    
    # Generate run ID
    timestamp = datetime.now()
    run_id = f"TER-{timestamp.strftime('%Y%m%d-%H%M')}-{git_info['short_sha']}"
    
    print(f"\n{'='*60}")
    print(f"LLMHub Test Execution Report")
    print(f"{'='*60}")
    print(f"Run ID: {run_id}")
    print(f"Workspace: {workspace_root}")
    print(f"{'='*60}\n")
    
    # Run pytest
    exit_code, xml_path = run_pytest_with_xml(workspace_root)
    
    # Parse results
    print("\nParsing test results...")
    test_data = parse_junit_xml(xml_path)
    
    # Build TER JSON
    ter_data = {
        "project": "llm-hub",
        "run_id": run_id,
        "commit": git_info["commit"],
        "branch": git_info["branch"],
        "timestamp": timestamp.isoformat(),
        "environment": {
            "python_version": platform.python_version(),
            "os": f"{platform.system()} {platform.release()}",
            "llmhub_version": get_llmhub_version()
        },
        "summary": test_data["summary"],
        "suites": test_data["suites"]
    }
    
    # Save JSON report
    reports_dir = workspace_root / "reports" / "test-execution"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = reports_dir / f"{run_id}.json"
    with open(json_path, "w") as f:
        json.dump(ter_data, f, indent=2)
    
    print(f"\n✓ JSON report saved: {json_path}")
    
    # Generate and save Markdown report
    md_report = generate_markdown_report(ter_data)
    md_path = reports_dir / f"{run_id}.md"
    with open(md_path, "w") as f:
        f.write(md_report)
    
    print(f"✓ Markdown report saved: {md_path}")
    
    # Print summary
    summary = ter_data["summary"]
    print(f"\n{'='*60}")
    print(f"Test Summary")
    print(f"{'='*60}")
    print(f"Status: {summary['status'].upper()}")
    print(f"Total:  {summary['total_tests']}")
    print(f"Passed: {summary['passed']} ✓")
    print(f"Failed: {summary['failed']} ✗")
    print(f"Skipped: {summary['skipped']} ⊘")
    print(f"Duration: {summary['duration_seconds']}s")
    print(f"{'='*60}\n")
    
    # Clean up temp XML
    if xml_path.exists():
        xml_path.unlink()
    
    # Exit with pytest exit code
    if summary['status'] != 'passed':
        print(f"❌ Tests failed. See report for details.")
        sys.exit(1)
    else:
        print(f"✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
