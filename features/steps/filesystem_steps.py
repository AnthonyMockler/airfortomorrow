from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path

from behave import given, then, when


REQUIRED_ENV_KEYS = [
    "HIMAWARI_FTP_USER",
    "HIMAWARI_FTP_PASSWORD",
    "CDSAPI_URL",
    "CDSAPI_KEY",
    "OPENAQ_API_KEY",
]

COMPONENT_LOG_PREFIXES = ("openaq_realtime_", "integrated_realtime_pipeline_")

AUTH_FAILURE_PATTERNS = [
    re.compile(r"Invalid credentials", re.IGNORECASE),
    re.compile(r"\bHTTP\s*401\b", re.IGNORECASE),
    re.compile(r"\bHTTP\s*403\b", re.IGNORECASE),
    re.compile(r"NotAuthorized", re.IGNORECASE),
    re.compile(r"Login incorrect", re.IGNORECASE),
    re.compile(r"FTP username and password must be provided", re.IGNORECASE),
]


def _resolve_path(context, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return context.repo_root / candidate


@given('the file "{path}" should exist')
def step_file_should_exist(context, path: str):
    resolved = _resolve_path(context, path)
    assert resolved.exists(), f"Path does not exist: {resolved}"
    assert resolved.is_file(), f"Path is not a file: {resolved}"


@then('the file "{path}" should contain "{text}"')
def step_file_should_contain(context, path: str, text: str):
    resolved = _resolve_path(context, path)
    assert resolved.exists(), f"Path does not exist: {resolved}"
    content = resolved.read_text(encoding="utf-8")
    assert text in content, f"Text not found in {resolved}: {text}"


@given("I create a temporary quickstart workspace")
def step_create_temp_quickstart_workspace(context):
    workspace = Path(tempfile.mkdtemp(prefix="air_quality_quickstart_"))
    context.quickstart_workspace = workspace


@when('I copy "{source}" to "{destination}" in the temporary quickstart workspace')
def step_copy_to_temp_quickstart_workspace(context, source: str, destination: str):
    source_path = _resolve_path(context, source)
    destination_path = context.quickstart_workspace / destination
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination_path)


@then('the path "{path}" in the temporary quickstart workspace should be a regular file')
def step_temp_workspace_file(context, path: str):
    resolved = context.quickstart_workspace / path
    assert resolved.exists(), f"Path does not exist: {resolved}"
    assert resolved.is_file(), f"Path is not a file: {resolved}"


@then('the temporary quickstart ".env" file should contain required credential keys')
def step_temp_workspace_env_contains_required_keys(context):
    env_path = context.quickstart_workspace / ".env"
    content = env_path.read_text(encoding="utf-8")
    missing_keys = [key for key in REQUIRED_ENV_KEYS if key not in content]
    assert not missing_keys, f"Missing keys in {env_path}: {missing_keys}"


@then("the command output should reference an existing log file")
def step_command_output_has_log_file(context):
    result = context.last_result
    assert result is not None, "No command has been executed in this scenario."
    match = re.search(r"Log file:\s*(.+)", result.output)
    assert match is not None, f"No log file reference found.\n{result.output}"
    log_path_text = match.group(1).strip()
    log_path = _resolve_path(context, log_path_text)
    assert log_path.exists(), f"Referenced log file does not exist: {log_path}"
    assert log_path.is_file(), f"Referenced log path is not a file: {log_path}"
    context.last_referenced_log_path = log_path


@then("the current run should generate OpenAQ and Himawari component logs")
def step_current_run_has_component_logs(context):
    result = context.last_result
    assert result is not None, "No command has been executed in this scenario."
    assert result.new_log_files, "No new log files were created during this command."

    new_log_names = [Path(log_path).name for log_path in result.new_log_files]
    missing_prefixes = [
        prefix
        for prefix in COMPONENT_LOG_PREFIXES
        if not any(name.startswith(prefix) for name in new_log_names)
    ]
    assert not missing_prefixes, (
        "Expected component logs were not created. "
        f"Missing prefixes: {missing_prefixes}. "
        f"New logs: {new_log_names}"
    )


@then("the current run logs should not contain authentication or credential failures")
def step_current_run_logs_no_auth_failures(context):
    result = context.last_result
    assert result is not None, "No command has been executed in this scenario."

    candidate_logs = [
        _resolve_path(context, relative_log_path)
        for relative_log_path in result.new_log_files
    ]

    referenced_log_path = getattr(context, "last_referenced_log_path", None)
    if referenced_log_path is not None and referenced_log_path not in candidate_logs:
        candidate_logs.append(referenced_log_path)

    assert candidate_logs, "No candidate log files found for authentication checks."

    failures = []
    for log_path in candidate_logs:
        if not log_path.exists() or not log_path.is_file():
            continue
        content = log_path.read_text(encoding="utf-8", errors="ignore")
        for pattern in AUTH_FAILURE_PATTERNS:
            match = pattern.search(content)
            if match:
                failures.append(
                    f"{log_path}: matched '{pattern.pattern}' around '{match.group(0)}'"
                )
                break

    assert not failures, (
        "Detected authentication/credential failures in logs for this run:\n"
        + "\n".join(failures)
    )


@then('the directory "{path}" should contain at least {count:d} files matching "{pattern}"')
def step_directory_contains_matching_files(context, path: str, count: int, pattern: str):
    directory = _resolve_path(context, path)
    assert directory.exists(), f"Directory does not exist: {directory}"
    assert directory.is_dir(), f"Path is not a directory: {directory}"
    matches = list(directory.glob(pattern))
    assert len(matches) >= count, (
        f"Expected at least {count} files matching {pattern} in {directory}, "
        f"found {len(matches)}"
    )
