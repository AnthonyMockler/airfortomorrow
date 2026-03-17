#!/usr/bin/env python3
"""
Run the Docker Behave harness with strict Tier A/B/C scenario selection.
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
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
FEATURES_RE = re.compile(r"^\d+\s+features?\s+.+$")
SCENARIOS_RE = re.compile(r"^\d+\s+scenarios?\s+.+$")
STEPS_RE = re.compile(r"^\d+\s+steps?\s+.+$")
RUNTIME_RE = re.compile(r"^Took\s+.+$")
FAILING_SCENARIO_RE = re.compile(r"^\s*features/.*:\d+\s*$")
STATUS_COUNT_RE = re.compile(r"(?P<count>\d+)\s+(?P<status>[A-Za-z_]+)")
TAG_TOKEN_RE = re.compile(r"@[A-Za-z0-9_.-]+")
FEATURE_DECL_RE = re.compile(r"^Feature:\s*(?P<name>.+)$", re.IGNORECASE)
SCENARIO_DECL_RE = re.compile(r"^Scenario(?: Outline)?:\s*(?P<name>.+)$", re.IGNORECASE)

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
LONG_RUN_CHECK_MINUTES = 10

TIER_TAG_TO_NAME = {
    "@tier_a": "A",
    "@tier_b": "B",
    "@tier_c": "C",
}
SCOPE_TO_TAG = {
    "all": None,
    "smoke": "@smoke",
    "contract": "@contract",
    "quickstart": "@quickstart",
    "regression": "@regression",
    "static_assets": "@static_assets",
}
BAD_STRICT_STATUSES = ("failed", "error", "errors", "undefined", "pending", "untested")


class TierValidationError(RuntimeError):
    """Raised when scenario tiering metadata is invalid."""


@dataclass(frozen=True)
class ScenarioRef:
    path: Path
    line: int
    name: str
    tags: frozenset[str]
    tier: str
    reported_instances: int

    @property
    def selector(self) -> str:
        return f"{self.path.as_posix()}:{self.line}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run tiered Behave suites in Docker with compact output and strict checks."
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
        "--tier",
        choices=("a", "b", "c", "all"),
        default="a",
        help=(
            "Tier to run: "
            "A=fast/local, B=live non-slow, C=slow. "
            "Use 'all' to run A then B then C."
        ),
    )
    parser.add_argument(
        "--scope",
        choices=tuple(SCOPE_TO_TAG.keys()),
        default="all",
        help=(
            "Optional fixed subset within a tier. "
            "This replaces ad-hoc --tags forwarding."
        ),
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List selected scenario selectors and exit without running Behave.",
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
        help="Behave formatter to inject before tier filters. Defaults to progress.",
    )
    parser.add_argument(
        "--raw-log",
        help=(
            "Write raw output to this file. "
            "When --tier=all, tier suffixes are appended to the filename."
        ),
    )
    parser.add_argument(
        "--tail-lines",
        type=int,
        default=60,
        help="Number of fallback lines to keep when no failure block is detected.",
    )
    parser.add_argument(
        "--long-run",
        action="store_true",
        help=(
            "Announce delayed-check guidance before starting the run. "
            "Tier C auto-enables this guidance."
        ),
    )
    parser.add_argument(
        "--no-compact-defaults",
        action="store_true",
        help="Do not inject compact Behave flags (-f/-q/-T/-c).",
    )
    return parser.parse_args()


def resolve_repo(path: str) -> Path:
    repo = Path(path).expanduser().resolve()
    harness = repo / "scripts" / "run_behave_tests.sh"
    if not harness.exists():
        raise SystemExit(
            f"Could not find Behave harness at {harness}. "
            "Run this from the repo root or pass --repo."
        )
    return repo


def build_raw_log_path(raw_log: str | None, tier: str, multi_tier: bool) -> Path:
    if raw_log:
        base_path = Path(raw_log).expanduser().resolve()
        base_path.parent.mkdir(parents=True, exist_ok=True)
        if not multi_tier:
            return base_path

        suffix = base_path.suffix or ".log"
        stem = base_path.stem if base_path.suffix else base_path.name
        return base_path.with_name(f"{stem}-tier-{tier.lower()}{suffix}")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path(tempfile.gettempdir()) / f"airfortomorrow-behave-tier-{tier.lower()}-{stamp}.log"


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


def should_enable_long_run_mode(
    args: argparse.Namespace,
    tier: str,
) -> tuple[bool, str | None]:
    if args.long_run:
        return True, "explicit --long-run"

    if tier == "C":
        return True, "tier C includes @slow scenarios"

    return False, None


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


def parse_status_counts(summary_line: str | None) -> dict[str, int]:
    if not summary_line:
        return {}

    counts: dict[str, int] = {}
    for match in STATUS_COUNT_RE.finditer(summary_line):
        status = match.group("status").lower()
        counts[status] = counts.get(status, 0) + int(match.group("count"))
    return counts


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
    scenario_counts = parse_status_counts(scenarios)
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
        "scenario_counts": scenario_counts,
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
    tier: str,
    scope: str,
    expected_selected_scenarios: int,
    expected_reported_scenarios: int,
    expected_skipped_scenarios: int,
) -> None:
    print(f"Tier: {tier}")
    print(f"Scope: {scope}")
    print(f"Expected selected scenarios: {expected_selected_scenarios}")
    print(f"Expected reported scenarios: {expected_reported_scenarios}")
    print(f"Expected framework skipped scenarios: {expected_skipped_scenarios}")
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


def print_long_run_preamble(raw_log_path: Path, reason: str) -> None:
    now = datetime.now().astimezone()
    next_check = now + timedelta(minutes=LONG_RUN_CHECK_MINUTES)
    tz_name = now.tzname() or "local"

    print(f"Long-run mode: enabled ({reason})", flush=True)
    print(
        "Polling cadence: no more often than every 5 to 10 minutes unless the run exits, fails, or materially changes state.",
        flush=True,
    )
    print(f"Started at: {now.strftime('%Y-%m-%d %H:%M:%S')} {tz_name}", flush=True)
    print(
        f"Next check after: {next_check.strftime('%Y-%m-%d %H:%M:%S')} {tz_name}",
        flush=True,
    )
    print(f"Raw log: {raw_log_path}", flush=True)


def extract_tags(tag_line: str) -> set[str]:
    return set(TAG_TOKEN_RE.findall(tag_line))


def resolve_scenario_tier(
    tags: set[str],
    feature_path: Path,
    line_number: int,
    scenario_name: str,
) -> str:
    tier_tags = sorted(tag for tag in tags if tag in TIER_TAG_TO_NAME)
    if len(tier_tags) != 1:
        raise TierValidationError(
            f"{feature_path}:{line_number} ({scenario_name}) must include exactly one "
            f"tier tag from {sorted(TIER_TAG_TO_NAME)}; found {tier_tags or 'none'}."
        )

    tier = TIER_TAG_TO_NAME[tier_tags[0]]
    has_live = "@live" in tags
    has_slow = "@slow" in tags

    if tier == "A" and (has_live or has_slow):
        raise TierValidationError(
            f"{feature_path}:{line_number} ({scenario_name}) uses @tier_a but also "
            "contains @live/@slow. Tier A must be local and non-slow."
        )
    if tier == "B" and (not has_live or has_slow):
        raise TierValidationError(
            f"{feature_path}:{line_number} ({scenario_name}) uses @tier_b but must "
            "contain @live and must not contain @slow."
        )
    if tier == "C" and not has_slow:
        raise TierValidationError(
            f"{feature_path}:{line_number} ({scenario_name}) uses @tier_c but must "
            "contain @slow."
        )
    return tier


def discover_scenarios(repo: Path) -> tuple[list[ScenarioRef], dict[Path, int]]:
    features_dir = repo / "features"
    if not features_dir.exists():
        raise TierValidationError(f"Missing features directory: {features_dir}")

    scenarios: list[ScenarioRef] = []
    feature_reported_totals: dict[Path, int] = {}
    for feature_path in sorted(features_dir.rglob("*.feature")):
        relative_feature_path = feature_path.relative_to(repo)
        feature_tags: set[str] = set()
        pending_tags: set[str] = set()
        lines = feature_path.read_text(encoding="utf-8", errors="replace").splitlines()
        feature_reported_total = 0
        current_scenario: dict[str, object] | None = None
        current_outline_rows = 0
        in_examples = False
        examples_header_seen = False

        def finalize_current_scenario() -> None:
            nonlocal current_scenario
            nonlocal current_outline_rows
            nonlocal in_examples
            nonlocal examples_header_seen
            nonlocal feature_reported_total

            if current_scenario is None:
                return

            scenario_name = str(current_scenario["name"])
            line_number = int(current_scenario["line"])
            combined_tags = set(current_scenario["tags"])
            is_outline = bool(current_scenario["is_outline"])

            tier = resolve_scenario_tier(
                combined_tags,
                relative_feature_path,
                line_number,
                scenario_name,
            )

            reported_instances = current_outline_rows if is_outline and current_outline_rows > 0 else 1
            scenarios.append(
                ScenarioRef(
                    path=relative_feature_path,
                    line=line_number,
                    name=scenario_name,
                    tags=frozenset(combined_tags),
                    tier=tier,
                    reported_instances=reported_instances,
                )
            )
            feature_reported_total += reported_instances

            current_scenario = None
            current_outline_rows = 0
            in_examples = False
            examples_header_seen = False

        for line_number, raw_line in enumerate(lines, start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                continue

            if stripped.startswith("@"):
                pending_tags.update(extract_tags(stripped))
                continue

            if FEATURE_DECL_RE.match(stripped):
                finalize_current_scenario()
                feature_tags = set(pending_tags)
                pending_tags.clear()
                continue

            scenario_match = SCENARIO_DECL_RE.match(stripped)
            if scenario_match:
                finalize_current_scenario()
                combined_tags = set(feature_tags)
                combined_tags.update(pending_tags)
                pending_tags.clear()
                scenario_name = scenario_match.group("name").strip()
                current_scenario = {
                    "name": scenario_name,
                    "line": line_number,
                    "tags": combined_tags,
                    "is_outline": stripped.lower().startswith("scenario outline:"),
                }
                continue

            if current_scenario and bool(current_scenario["is_outline"]):
                lowered = stripped.lower()
                if lowered.startswith("examples:"):
                    in_examples = True
                    examples_header_seen = False
                    pending_tags.clear()
                    continue
                if in_examples and stripped.startswith("|"):
                    if examples_header_seen:
                        current_outline_rows += 1
                    else:
                        examples_header_seen = True
                    continue
                if in_examples and not stripped.startswith("|"):
                    in_examples = False
                    examples_header_seen = False

            # Do not leak tags onto unrelated blocks.
            if pending_tags:
                pending_tags.clear()

        finalize_current_scenario()
        feature_reported_totals[relative_feature_path] = feature_reported_total

    if not scenarios:
        raise TierValidationError("No Behave scenarios found under features/.")
    return scenarios, feature_reported_totals


def select_scenarios(
    all_scenarios: list[ScenarioRef],
    tier: str,
    scope: str,
) -> list[ScenarioRef]:
    scope_tag = SCOPE_TO_TAG[scope]
    selected = [
        scenario
        for scenario in all_scenarios
        if scenario.tier == tier and (scope_tag is None or scope_tag in scenario.tags)
    ]
    if not selected:
        raise TierValidationError(
            f"No scenarios matched tier {tier} and scope {scope!r}. "
            "Either tagging is wrong or the scope is too narrow."
        )
    return sorted(selected, key=lambda item: (item.path.as_posix(), item.line))


def print_selected_scenarios(
    tier: str,
    scope: str,
    selected: list[ScenarioRef],
) -> None:
    print(f"Tier {tier} | scope={scope} | selected={len(selected)}")
    for scenario in selected:
        print(f"- {scenario.selector} :: {scenario.name}")


def validate_strict_outcome(
    tier: str,
    expected_selected_scenarios: int,
    expected_reported_scenarios: int,
    expected_skipped_scenarios: int,
    behave_returncode: int,
    summary: dict[str, object],
) -> list[str]:
    errors: list[str] = []
    if behave_returncode != 0:
        errors.append(f"Behave exited non-zero: {behave_returncode}")

    scenarios_line = summary.get("scenarios")
    scenario_counts = summary.get("scenario_counts")
    parsed_counts = scenario_counts if isinstance(scenario_counts, dict) else {}

    if not scenarios_line:
        errors.append("Could not find Behave scenarios summary line.")
    elif not parsed_counts:
        errors.append(f"Could not parse scenario counts from: {scenarios_line!r}")
    else:
        observed_total = sum(parsed_counts.values())
        if observed_total != expected_reported_scenarios:
            errors.append(
                f"Expected {expected_reported_scenarios} reported scenarios for tier {tier}, "
                f"but Behave reported {observed_total}."
            )

        skipped = parsed_counts.get("skipped", 0)
        if skipped != expected_skipped_scenarios:
            errors.append(
                f"Expected {expected_skipped_scenarios} framework skips for tier {tier}, "
                f"but observed {skipped}."
            )

        executed = observed_total - skipped
        if executed != expected_selected_scenarios:
            errors.append(
                f"Expected {expected_selected_scenarios} selected scenarios to execute in tier {tier}, "
                f"but observed {executed}."
            )

        for status in BAD_STRICT_STATUSES:
            count = parsed_counts.get(status, 0)
            if count > 0:
                errors.append(f"Detected {count} scenarios with status '{status}'.")

    if errors:
        print("Strict checks: FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        print("Strict checks: PASS")

    return errors


def run_tier(
    repo: Path,
    args: argparse.Namespace,
    tier: str,
    scope: str,
    selected: list[ScenarioRef],
    feature_scenario_totals: dict[Path, int],
    multi_tier: bool,
) -> int:
    selected_feature_paths = {scenario.path for scenario in selected}
    expected_selected_scenarios = sum(scenario.reported_instances for scenario in selected)
    expected_reported_scenarios = sum(
        feature_scenario_totals[path] for path in selected_feature_paths
    )
    expected_skipped_scenarios = expected_reported_scenarios - expected_selected_scenarios

    tier_tag = f"@tier_{tier.lower()}"
    scope_tag = SCOPE_TO_TAG[scope]
    feature_filters = sorted(path.as_posix() for path in selected_feature_paths)

    raw_log_path = build_raw_log_path(args.raw_log, tier, multi_tier)
    behave_args = ["--tags", tier_tag]
    if scope_tag:
        behave_args.extend(["--tags", scope_tag])
    behave_args.extend(feature_filters)
    command = build_command(repo, args, behave_args)
    long_run_mode, long_run_reason = should_enable_long_run_mode(args, tier)

    if long_run_mode:
        print_long_run_preamble(
            raw_log_path,
            long_run_reason or "long-running tiered Behave invocation",
        )

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
    print_summary(
        summary=summary,
        repo=repo,
        command=command,
        raw_log_path=raw_log_path,
        tier=tier,
        scope=scope,
        expected_selected_scenarios=expected_selected_scenarios,
        expected_reported_scenarios=expected_reported_scenarios,
        expected_skipped_scenarios=expected_skipped_scenarios,
    )

    errors = validate_strict_outcome(
        tier=tier,
        expected_selected_scenarios=expected_selected_scenarios,
        expected_reported_scenarios=expected_reported_scenarios,
        expected_skipped_scenarios=expected_skipped_scenarios,
        behave_returncode=completed.returncode,
        summary=summary,
    )
    return 1 if errors else 0


def main() -> int:
    args = parse_args()
    repo = resolve_repo(args.repo)

    try:
        all_scenarios, feature_reported_totals = discover_scenarios(repo)
    except TierValidationError as exc:
        print(f"Tier configuration error: {exc}", file=sys.stderr)
        return 2

    requested_tier = args.tier.upper()
    tiers = ["A", "B", "C"] if requested_tier == "ALL" else [requested_tier]

    exit_code = 0
    for index, tier in enumerate(tiers):
        try:
            selected = select_scenarios(all_scenarios, tier=tier, scope=args.scope)
        except TierValidationError as exc:
            print(f"Tier selection error: {exc}", file=sys.stderr)
            return 2

        if args.list:
            print_selected_scenarios(tier=tier, scope=args.scope, selected=selected)
            continue

        current_code = run_tier(
            repo=repo,
            args=args,
            tier=tier,
            scope=args.scope,
            selected=selected,
            feature_scenario_totals=feature_reported_totals,
            multi_tier=len(tiers) > 1,
        )
        if current_code != 0:
            exit_code = current_code
            if index < len(tiers) - 1:
                print("Aborting remaining tiers after first failure.")
            break

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
