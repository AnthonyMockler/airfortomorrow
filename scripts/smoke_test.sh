#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    cat <<'EOF'
Run Tier A smoke scenarios through the compact Behave runner.

Usage:
  ./scripts/smoke_test.sh [compact runner options...]

Examples:
  ./scripts/smoke_test.sh
  ./scripts/smoke_test.sh --build
  ./scripts/smoke_test.sh --image airquality-app:test

Behavior:
  - Runs only scenarios tagged as Tier A + @smoke.
  - Delegates to ./scripts/run_behave_tests_compact.sh.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
fi

exec "$SCRIPT_DIR/run_behave_tests_compact.sh" --tier a --scope smoke "$@"
