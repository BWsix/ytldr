#!/usr/bin/env python3
"""
Test runner for ytldr project.
"""

import sys
import subprocess
import argparse


def run_tests(test_type, coverage=False, verbose=False):
    """Run tests with specified options."""
    
    cmd = ["python", "-m", "pytest"]
    
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    elif test_type == "all":
        pass  # Run all tests
    else:
        print(f"Unknown test type: {test_type}")
        return False
    
    if coverage:
        cmd.extend(["--cov=ytldr", "--cov-report=term-missing"])
    
    if verbose:
        cmd.append("-v")
    
    print(f"Running tests: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with exit code: {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run ytldr tests")
    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "fast", "all"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    success = run_tests(args.test_type, args.coverage, args.verbose)
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 