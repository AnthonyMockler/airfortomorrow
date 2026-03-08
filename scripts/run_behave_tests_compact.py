#!/usr/bin/env python3
"""
Run the repository's Docker Behave harness with compact, agent-friendly output.
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
FEATURES_RE = re.compile(r"^\d+\s+features?\s+passed,.*$")
SCENARIOS_RE = re.compile(r"^\d+\s+scenarios?\s+passed,.*$")
STEPS_RE = re.compile(r"^\d+\s+steps?\s+passed,.*$")
RUNTIME_RE = re.compile(r"^Took\s+.+$")
FAILING_SCENARIO_RE = re.compile(r"^\s*features/.*:\d+\s*$")
KEY_FAILURE_PATTERNS = [
    re.compile(r"ASSERT FAILED", re.IGNORECASE),
    re.compile(r"AssertionError", re.IGNORECASE),
    re.compile(r"Traceback \(most recent call last\)", re.IGNORECASE),
    re.compile(r"\bERROR\b", re.IGNORECASE),
    re.compile(r"\bFAILED\b", re.IGNORECASE),
    re.compile(r"\bundefined\b", re.IGNORECASE),
    re.compile(r"command timed out", re.IGNORECASE),
]
GEMINI_INPUT_CHAR_LIMIT = 8000
GEMINI_TIMEOUT_SECONDS = 30


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description=(
            "Run ./scripts/run_behave_tests.sh with compact defaults and summarize the result."
        )
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to the Air for Tomorrow repository. Defaults to the current directory.",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Forward --build to the Docker Behave harness in host mode.",
    )
    parser.add_argument(
        "--image",
        help="Forward --image to the Docker Behave harness in host mode.",
    )
    parser.add_argument(
        "--gemini",
        choices=("auto", "always", "never"),
        default="auto",
        help=(
            "Use Gemini to denoise results. "
            "auto=failures only, always=all runs, never=local summary only."
        ),
    )
    parser.add_argument(
        "--formatter",
        default="progress",
        help="Behave formatter to inject before forwarded args. Defaults to progress.",
    )
    parser.add_argument(
        "--raw-log",
        help="Write the full raw output to this file instead of a temp file.",
    )
    parser.add_argument(
        "--tail-lines",
        type=int,
        default=60,
        help="Number of fallback lines to keep when no failure block is detected.",
    )
    parser.add_argument(
        "--no-compact-defaults",
        action="store_true",
        help="Do not inject compact Behave flags (-f/-q/-T/-c).",
    )
    return parser.parse_known_args()


def resolve_repo(path: str) -> Path:
    repo = Path(path).expanduser().resolve()
    harness = repo / "scripts" / "run_behave_tests.sh"
    if not harness.exists():
        raise SystemExit(
            f"Could not find Behave harness at {harness}. "
            "Run this from the repo root or pass --repo."
        )
    return repo


def build_raw_log_path(raw_log: str | None) -> Path:
    if raw_log:
        path = Path(raw_log).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path(tempfile.gettempdir()) / f"airfortomorrow-behave-{stamp}.log"


def running_inside_docker() -> bool:
    return os.getenv("AIR_QUALITY_TEST_IN_DOCKER") == "1" or Path("/.dockerenv").exists()


def build_command(
    repo: Path,
    args: argparse.Namespace,
    behave_args: list[str],
) -> list[str]:
    command = [str(repo / "scripts" / "run_behave_tests.sh")]
    inside_docker = running_inside_docker()

    if inside_docker:
        if args.build:
            raise SystemExit("Error: --build cannot be used when already inside Docker.")
        if args.image:
            raise SystemExit("Error: --image cannot be used when already inside Docker.")
        command.append("--inside")
    else:
        if args.build:
            command.append("--build")
        if args.image:
            command.extend(["--image", args.image])
        command.append("--")

    compact_args: list[str] = []
    if not args.no_compact_defaults:
        compact_args.extend(["-f", args.formatter, "-q", "-T", "-c"])

    command.extend(compact_args)
    command.extend(behave_args)
    return command


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_RE.sub("", text)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def find_last_matching(lines: list[str], pattern: re.Pattern[str]) -> str | None:
    for line in reversed(lines):
        if pattern.match(line.strip()):
            return line.strip()
    return None


def extract_failing_scenarios(lines: list[str]) -> list[str]:
    failing: list[str] = []
    in_block = False

    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped == "Failing scenarios:":
            in_block = True
            continue
        if not in_block:
            continue
        if not stripped:
            if failing:
                break
            continue
        if FAILING_SCENARIO_RE.match(stripped):
            failing.append(stripped)
            continue
        if failing:
            break

    return failing


def collapse_blank_runs(lines: list[str]) -> list[str]:
    collapsed: list[str] = []
    previous_blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank and previous_blank:
            continue
        collapsed.append(line.rstrip())
        previous_blank = is_blank
    while collapsed and not collapsed[0].strip():
        collapsed.pop(0)
    while collapsed and not collapsed[-1].strip():
        collapsed.pop()
    return collapsed


def extract_local_excerpt(lines: list[str], tail_lines: int) -> list[str]:
    indexes = [
        index
        for index, line in enumerate(lines)
        if any(pattern.search(line) for pattern in KEY_FAILURE_PATTERNS)
    ]
    if not indexes:
        return collapse_blank_runs(lines[-tail_lines:])

    slices: list[str] = []
    seen: set[tuple[int, str]] = set()
    for index in indexes[-3:]:
        start = max(0, index - 2)
        end = min(len(lines), index + 5)
        for offset, line in enumerate(lines[start:end], start=start):
            marker = (offset, line)
            if marker in seen:
                continue
            seen.add(marker)
            slices.append(line)
    return collapse_blank_runs(slices)


def format_command(command: list[str], repo: Path) -> str:
    rendered: list[str] = []
    for item in command:
        try:
            path = Path(item)
        except Exception:
            rendered.append(shlex.quote(item))
            continue

        if path.is_absolute():
            try:
                rendered.append(shlex.quote(path.relative_to(repo).as_posix()))
                continue
            except ValueError:
                pass
        rendered.append(shlex.quote(item))
    return " ".join(rendered)


def gemini_available() -> bool:
    return shutil.which("gemini") is not None


def normalize_gemini_output(text: str) -> str:
    lines = [line.rstrip() for line in text.strip().splitlines() if line.strip()]
    bullet_indexes = [
        index
        for index, line in enumerate(lines)
        if line.lstrip().startswith(("-", "*"))
    ]
    if bullet_indexes:
        lines = lines[bullet_indexes[0]:]

    normalized = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("* "):
            normalized.append(f"- {stripped[2:]}")
        else:
            normalized.append(stripped)
    return "\n".join(normalized).strip()


def run_gemini(prompt: str, stdin_text: str) -> str | None:
    if not gemini_available():
        return None

    truncated_input = stdin_text[-GEMINI_INPUT_CHAR_LIMIT:]

    try:
        completed = subprocess.run(
            ["gemini", "-p", prompt, "-o", "text"],
            input=truncated_input,
            text=True,
            capture_output=True,
            check=False,
            timeout=GEMINI_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    if completed.returncode != 0:
        return None

    output = normalize_gemini_output(completed.stdout)
    return output or None


def build_gemini_prompt(outcome: str) -> str:
    return (
        "Denoise this Air for Tomorrow Behave test output. "
        f"The run outcome is {outcome}. "
        "Return only plain text bullet points, with no intro sentence or conclusion. "
        "Use at most 6 bullet points. "
        "Keep only concrete facts from the input. "
        "Include counts/runtime if present, failing scenario paths if present, "
        "and the first actionable failure signal. "
        "If the issue is a Docker or harness failure rather than a Behave assertion, say that."
    )


def should_use_gemini(mode: str, returncode: int) -> bool:
    if mode == "never":
        return False
    if mode == "always":
        return True
    return returncode != 0


def summarize_output(
    output: str,
    returncode: int,
    tail_lines: int,
    gemini_mode: str,
) -> dict[str, object]:
    clean_output = strip_ansi(output)
    lines = clean_output.splitlines()

    features = find_last_matching(lines, FEATURES_RE)
    scenarios = find_last_matching(lines, SCENARIOS_RE)
    steps = find_last_matching(lines, STEPS_RE)
    runtime = find_last_matching(lines, RUNTIME_RE)
    failing_scenarios = extract_failing_scenarios(lines)

    has_behave_summary = any((features, scenarios, steps, runtime, failing_scenarios))
    if returncode == 0:
        outcome = "PASS"
    elif has_behave_summary:
        outcome = "FAIL"
    else:
        outcome = "ERROR"

    excerpt_lines = extract_local_excerpt(lines, tail_lines)

    gemini_summary = None
    if should_use_gemini(gemini_mode, returncode):
        summary_input_parts = []
        for label, value in (
            ("features", features),
            ("scenarios", scenarios),
            ("steps", steps),
            ("runtime", runtime),
        ):
            if value:
                summary_input_parts.append(f"{label}: {value}")
        if failing_scenarios:
            summary_input_parts.append("failing_scenarios:")
            summary_input_parts.extend(failing_scenarios)
        if excerpt_lines:
            summary_input_parts.append("excerpt:")
            summary_input_parts.extend(excerpt_lines)

        gemini_summary = run_gemini(
            build_gemini_prompt(outcome),
            "\n".join(summary_input_parts).strip(),
        )

    return {
        "outcome": outcome,
        "features": features,
        "scenarios": scenarios,
        "steps": steps,
        "runtime": runtime,
        "failing_scenarios": failing_scenarios,
        "excerpt_lines": excerpt_lines,
        "gemini_summary": gemini_summary,
    }


def print_summary(
    summary: dict[str, object],
    repo: Path,
    command: list[str],
    raw_log_path: Path,
) -> None:
    print(f"Outcome: {summary['outcome']}")
    print(f"Repo: {repo}")
    print(f"Command: {format_command(command, repo)}")

    for label in ("features", "scenarios", "steps", "runtime"):
        value = summary[label]
        if value:
            print(f"{label.capitalize()}: {value}")

    failing_scenarios = summary["failing_scenarios"]
    if failing_scenarios:
        print("Failing scenarios:")
        for item in failing_scenarios:
            print(f"- {item}")

    gemini_summary = summary["gemini_summary"]
    if gemini_summary:
        print("Gemini summary:")
        print(gemini_summary)
    else:
        excerpt_lines = summary["excerpt_lines"]
        if summary["outcome"] != "PASS" and excerpt_lines:
            print("Key output:")
            for line in excerpt_lines:
                print(line)

    print(f"Raw log: {raw_log_path}")


def main() -> int:
    args, behave_args = parse_args()
    repo = resolve_repo(args.repo)
    raw_log_path = build_raw_log_path(args.raw_log)
    command = build_command(repo, args, behave_args)

    with raw_log_path.open("w", encoding="utf-8") as handle:
        completed = subprocess.run(
            command,
            cwd=repo,
            stdout=handle,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

    output = read_text(raw_log_path)
    summary = summarize_output(
        output=output,
        returncode=completed.returncode,
        tail_lines=args.tail_lines,
        gemini_mode=args.gemini,
    )
    print_summary(summary, repo, command, raw_log_path)
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
