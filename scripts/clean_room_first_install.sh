#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

README_REPO_URL_DEFAULT="https://github.com/unicef/airfortomorrow.git"
DIND_IMAGE_DEFAULT="docker:27-dind"
DIND_READY_TIMEOUT_SECONDS=180

REPO_URL="$README_REPO_URL_DEFAULT"
KEEP_ISOLATION=false
DIND_IMAGE="$DIND_IMAGE_DEFAULT"

TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"
RUN_ID="cleanroom_${TIMESTAMP}_$$"
LOG_DIR="$BASE_DIR/logs/cleanroom/$RUN_ID"
RUN_LOG="$LOG_DIR/clean_room_run.log"
REPORT_FILE="$LOG_DIR/clean_room_report.txt"

DIND_NAME="airft_dind_${RUN_ID}"
DIND_NETWORK="airft_net_${RUN_ID}"

README_STATUS="SUCCESS"
FAILED_README_STEP=""
FAILED_COMMAND=""
FAILED_EXIT_CODE=0
FAILED_ERROR_LINE=""
REPO_PATH_IN_DIND=""

usage() {
    cat <<EOF
Run a strict README Quick Start replay in an isolated Docker-in-Docker environment.

Usage:
  ./scripts/clean_room_first_install.sh [options]

Options:
  --repo-url URL       Repository URL to clone (default: $README_REPO_URL_DEFAULT)
  --log-dir PATH       Output directory for logs/reports (default: logs/cleanroom/<run-id>)
  --dind-image IMAGE   docker:dind image to use (default: $DIND_IMAGE_DEFAULT)
  --keep-isolation     Keep the DinD container/network after run for debugging
  -h, --help           Show this help

Notes:
  - Install commands replay only README Quick Start commands.
  - The README docker run command is executed non-interactively (-i instead of -it)
    so this harness can feed the Step 4 commands via stdin.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo-url)
            if [[ $# -lt 2 ]]; then
                echo "Error: --repo-url requires a value." >&2
                exit 1
            fi
            REPO_URL="$2"
            shift 2
            ;;
        --log-dir)
            if [[ $# -lt 2 ]]; then
                echo "Error: --log-dir requires a value." >&2
                exit 1
            fi
            LOG_DIR="$2"
            RUN_LOG="$LOG_DIR/clean_room_run.log"
            REPORT_FILE="$LOG_DIR/clean_room_report.txt"
            shift 2
            ;;
        --dind-image)
            if [[ $# -lt 2 ]]; then
                echo "Error: --dind-image requires a value." >&2
                exit 1
            fi
            DIND_IMAGE="$2"
            shift 2
            ;;
        --keep-isolation)
            KEEP_ISOLATION=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Error: unknown option: $1" >&2
            usage
            exit 1
            ;;
    esac
done

mkdir -p "$LOG_DIR"
touch "$RUN_LOG"

log() {
    local message="$1"
    local now
    now="$(date +"%Y-%m-%d %H:%M:%S")"
    echo "[$now] $message" | tee -a "$RUN_LOG"
}

cleanup() {
    local cleanup_rc=0

    if [[ "$KEEP_ISOLATION" == true ]]; then
        log "Keeping isolation environment for debugging."
        log "  DinD container: $DIND_NAME"
        log "  DinD network:   $DIND_NETWORK"
        return 0
    fi

    if docker ps -a --format '{{.Names}}' | grep -Fxq "$DIND_NAME"; then
        docker rm -f "$DIND_NAME" >/dev/null 2>&1 || cleanup_rc=1
    fi

    if docker network ls --format '{{.Name}}' | grep -Fxq "$DIND_NETWORK"; then
        docker network rm "$DIND_NETWORK" >/dev/null 2>&1 || cleanup_rc=1
    fi

    if [[ $cleanup_rc -ne 0 ]]; then
        log "Warning: cleanup encountered errors."
    fi
}

write_report() {
    local repo_size_kb="NA"
    local image_size_bytes="NA"
    local docker_data_root_kb="NA"

    if docker ps -a --format '{{.Names}}' | grep -Fxq "$DIND_NAME"; then
        set +e
        repo_size_kb="$(docker exec "$DIND_NAME" sh -lc "if [ -n \"$REPO_PATH_IN_DIND\" ] && [ -d \"$REPO_PATH_IN_DIND\" ]; then du -sk \"$REPO_PATH_IN_DIND\" | cut -f1; else echo NA; fi" 2>/dev/null)"
        image_size_bytes="$(docker exec "$DIND_NAME" sh -lc "docker image inspect airquality-app --format '{{.Size}}' 2>/dev/null || echo NA" 2>/dev/null)"
        docker_data_root_kb="$(docker exec "$DIND_NAME" sh -lc "du -sk /var/lib/docker 2>/dev/null | cut -f1" 2>/dev/null)"
        set -e
    fi

    cat > "$REPORT_FILE" <<EOF
run_id=$RUN_ID
timestamp=$TIMESTAMP
repo_url=$REPO_URL
readme_replay_status=$README_STATUS
failed_readme_step=$FAILED_README_STEP
failed_command=$FAILED_COMMAND
failed_exit_code=$FAILED_EXIT_CODE
first_actionable_error_line=$FAILED_ERROR_LINE
repo_size_kb=$repo_size_kb
airquality_image_size_bytes=$image_size_bytes
dind_data_root_kb=$docker_data_root_kb
log_dir=$LOG_DIR
run_log=$RUN_LOG
EOF
}

trap 'write_report; cleanup' EXIT INT TERM

if ! command -v docker >/dev/null 2>&1; then
    echo "Error: docker is required on host to run clean-room harness." >&2
    exit 1
fi

run_dind_command() {
    local readme_step="$1"
    local description="$2"
    local command="$3"
    local step_log="$LOG_DIR/readme_step_${readme_step//./_}.log"

    log "README Step $readme_step: $description"
    log "Command: $command"

    set +e
    docker exec "$DIND_NAME" sh -lc "$command" 2>&1 | tee "$step_log" | tee -a "$RUN_LOG"
    local cmd_rc=${PIPESTATUS[0]}
    set -e

    if [[ $cmd_rc -ne 0 ]]; then
        README_STATUS="FAILED"
        FAILED_README_STEP="$readme_step"
        FAILED_COMMAND="$command"
        FAILED_EXIT_CODE="$cmd_rc"
        FAILED_ERROR_LINE="$(grep -m1 -Ei 'error|failed|not found|no such file|cannot|denied|missing|traceback' "$step_log" || true)"
        if [[ -z "$FAILED_ERROR_LINE" ]]; then
            FAILED_ERROR_LINE="$(sed -n '/./{p;q;}' "$step_log" || true)"
        fi
        return $cmd_rc
    fi

    return 0
}

run_readme_step_or_exit() {
    local step="$1"
    local description="$2"
    local command="$3"
    if ! run_dind_command "$step" "$description" "$command"; then
        log "README Step $step failed with exit code $FAILED_EXIT_CODE."
        exit "$FAILED_EXIT_CODE"
    fi
}

log "Starting clean-room README replay harness."
log "Run ID: $RUN_ID"
log "Log directory: $LOG_DIR"

log "Creating isolated Docker network: $DIND_NETWORK"
docker network create "$DIND_NETWORK" >/dev/null

log "Starting DinD container: $DIND_NAME"
docker run -d --privileged \
    --name "$DIND_NAME" \
    --network "$DIND_NETWORK" \
    --network-alias dind \
    -e DOCKER_TLS_CERTDIR= \
    "$DIND_IMAGE" \
    --host=tcp://0.0.0.0:2375 \
    --host=unix:///var/run/docker.sock >/dev/null

log "Waiting for isolated Docker daemon to become ready..."
for _ in $(seq 1 "$DIND_READY_TIMEOUT_SECONDS"); do
    if docker exec "$DIND_NAME" sh -lc 'docker info >/dev/null 2>&1'; then
        log "Isolated Docker daemon is ready."
        break
    fi
    sleep 1
done

if ! docker exec "$DIND_NAME" sh -lc 'docker info >/dev/null 2>&1'; then
    README_STATUS="FAILED"
    FAILED_README_STEP="HARNESS_INIT"
    FAILED_COMMAND="wait_for_dind"
    FAILED_EXIT_CODE=1
    FAILED_ERROR_LINE="Timed out waiting for isolated Docker daemon readiness."
    exit 1
fi

log "Installing tooling in isolated environment (git, git-lfs)."
docker exec "$DIND_NAME" sh -lc 'apk add --no-cache bash git git-lfs coreutils'

REPO_NAME="$(basename "$REPO_URL")"
REPO_NAME="${REPO_NAME%.git}"
WORKSPACE_ROOT="/workspace"
REPO_PATH_IN_DIND="$WORKSPACE_ROOT/$REPO_NAME"

# README Step 1: Clone + git lfs install + git lfs pull
run_readme_step_or_exit \
    "1.1" \
    "Clone the repository" \
    "mkdir -p '$WORKSPACE_ROOT' && cd '$WORKSPACE_ROOT' && git clone '$REPO_URL'"

run_readme_step_or_exit \
    "1.2" \
    "Initialize Git LFS" \
    "cd '$REPO_PATH_IN_DIND' && git lfs install"

run_readme_step_or_exit \
    "1.3" \
    "Pull Git LFS objects" \
    "cd '$REPO_PATH_IN_DIND' && git lfs pull"

# README Step 2: Configure credentials template
run_readme_step_or_exit \
    "2" \
    "Create .env from env_template" \
    "cd '$REPO_PATH_IN_DIND' && cp env_template .env"

# README Step 3: Build image
run_readme_step_or_exit \
    "3.1" \
    "Build Docker image" \
    "cd '$REPO_PATH_IN_DIND' && docker build -t airquality-app ."

# README Step 3/4 replay:
# README uses `docker run --rm -it ... airquality-app`, then manual commands inside.
# For automation, this harness uses `-i` and feeds the exact Step 4 commands via stdin.
README_CONTAINER_REPLAY_CMD='cd "'"$REPO_PATH_IN_DIND"'" && printf "%s\n%s\n" "./scripts/setup.sh" "./scripts/run_complete_pipeline.sh --mode realtime --countries THA LAO --generate-maps --parallel" | docker run --rm -i --memory=16g -v "$(pwd)/data:/app/data" -v "$(pwd)/assets:/app/assets" -v "$(pwd)/scripts:/app/scripts" -v "$(pwd)/config:/app/config" -v "$(pwd)/src:/app/src" -v "$(pwd)/.env:/app/.env" -e LOCAL_DEV=1 airquality-app'

run_readme_step_or_exit \
    "3.2+4" \
    "Run container and execute README first prediction commands" \
    "$README_CONTAINER_REPLAY_CMD"

log "README replay completed successfully."
exit 0
