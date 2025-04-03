import shutil
import subprocess
import sys
from pathlib import Path

SERVICES = ["user_service", "product_service", "order_service"]
ROOT = Path(__file__).resolve().parent.parent


# Cleanup before running
for service in SERVICES:
    coverage_file = ROOT / "services" / service / ".coverage"
    if coverage_file.exists():
        coverage_file.unlink()

htmlcov = ROOT / "htmlcov"
if htmlcov.exists():
    shutil.rmtree(htmlcov)


def run_pytest_with_coverage(service):
    service_path = ROOT / "services" / service
    print(f"🔍 Running tests for {service}...")
    result = subprocess.run(
        ["poetry", "run", "pytest", "--cov=app", "--cov-report=", "--cov-append"],
        cwd=service_path
    )
    return result.returncode


def combine_coverage():
    print("\n📊 Combining coverage reports...")
    result = subprocess.run(["coverage", "combine", "services/*/.coverage"], cwd=ROOT, shell=True)
    if result.returncode == 0:
        subprocess.run(["coverage", "report"], cwd=ROOT)
        subprocess.run(["coverage", "html"], cwd=ROOT)
    else:
        print("❌ Failed to combine coverage files")


def main():
    failures = []

    for service in SERVICES:
        exit_code = run_pytest_with_coverage(service)
        if exit_code != 0:
            failures.append(service)

    combine_coverage()

    if failures:
        print("\n❌ The following services had failing tests:")
        for f in failures:
            print(f"- {f}")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()
