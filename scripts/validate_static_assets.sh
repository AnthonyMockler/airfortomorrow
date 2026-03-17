#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

IMAGE_NAME="${AIR_QUALITY_TEST_IMAGE:-airquality-app:test}"
FORCE_BUILD=false
VALIDATOR_ARGS=()

usage() {
    cat <<'EOF'
Validate static/bootstrap parquet/CSV assets against the AQ pipeline loader contracts.

Usage:
  ./scripts/validate_static_assets.sh [--build] [--image <name>] [validator args...]

Examples:
  ./scripts/validate_static_assets.sh
  ./scripts/validate_static_assets.sh --sample-rows 500
  ./scripts/validate_static_assets.sh --build --sample-rows 1000

Options:
  --build           Force rebuild of the Docker image before running validation.
  --image <name>    Docker image tag to use/build (default: airquality-app:test).
  -h, --help        Show this help message.
EOF
}

require_inside_docker() {
    if [[ ! -f /.dockerenv ]]; then
        echo "Error: --inside is restricted to Docker containers." >&2
        echo "Run ./scripts/validate_static_assets.sh from host and let the wrapper launch Docker." >&2
        exit 1
    fi
}

run_inside() {
    require_inside_docker
    cd "$BASE_DIR"
    export PYTHONPATH="$BASE_DIR/src:${PYTHONPATH:-}"
    exec python "$BASE_DIR/src/validate_static_assets.py" "${VALIDATOR_ARGS[@]}"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --inside)
            shift
            VALIDATOR_ARGS=("$@")
            run_inside
            ;;
        --build)
            FORCE_BUILD=true
            shift
            ;;
        --image)
            if [[ $# -lt 2 ]]; then
                echo "Error: --image requires a value." >&2
                exit 1
            fi
            IMAGE_NAME="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            VALIDATOR_ARGS+=("$1")
            shift
            ;;
    esac
done

if [[ -f /.dockerenv ]]; then
    run_inside
fi

if ! command -v docker >/dev/null 2>&1; then
    echo "Error: Docker is required to validate static assets." >&2
    exit 1
fi

if [[ "$FORCE_BUILD" == "true" ]] || ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    echo "Building validation image: $IMAGE_NAME"
    docker build -t "$IMAGE_NAME" "$BASE_DIR"
fi

docker run --rm \
    --entrypoint /app/scripts/validate_static_assets.sh \
    -e AIR_QUALITY_TEST_IN_DOCKER=1 \
    -v "$BASE_DIR:/app" \
    -w /app \
    "$IMAGE_NAME" \
    --inside "${VALIDATOR_ARGS[@]}"
