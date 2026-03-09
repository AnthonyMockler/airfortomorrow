# Decision

Add a long-run mode to the compact Behave shim so it prints a durable raw-log path and explicit delayed re-check guidance before starting long-running test work.

# Why

The docs now tell agents to avoid frequent polling during performance-style test runs, but docs alone are soft enforcement. The compact shim is the preferred entrypoint for agent-driven Behave work and already manages the raw-log path, so it is the right place to surface an operational reminder at the moment a long-running run begins.

# Change Scope

- Add `--long-run` to the compact Behave shim help and CLI parsing.
- Print long-run execution guidance before the underlying harness starts, including raw-log location and a recommended next-check timestamp.
- Auto-enable the same guidance when forwarded Behave args include `@slow`.
- Add Behave contract coverage for the help text and the runtime guidance output.

# Non-Goals

- Do not change the Docker-backed raw Behave harness defaults.
- Do not add background process management or detached scheduling.
- Do not treat every Behave run as long-running by default.
