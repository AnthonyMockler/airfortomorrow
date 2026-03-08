# Feature Goal

Teach agents, via root `AGENTS.md`, to wait for long-running test and pipeline commands instead of polling frequently.

# Red

- Extend Behave contract coverage so root `AGENTS.md` must include the long-run waiting policy.
- Run the smallest targeted Behave command and capture the expected failure because that text is not present yet.

# Green

- Add a short `Long-Running Test Commands` section to root `AGENTS.md`.
- Keep the policy concrete and enforceable:
  - prefer the compact shim,
  - wait for completion,
  - poll no more often than once every 10-15 minutes for 30-90 minute runs,
  - avoid tailing logs or interim updates unless needed.

# Regression Safety

- Re-run the targeted contract feature after updating `AGENTS.md`.
- Confirm the earlier compact-shim guidance still passes in the same feature.

# Success Criteria

- Root `AGENTS.md` explicitly tells agents to start long-running test commands once and wait for completion.
- Root `AGENTS.md` sets a polling ceiling for long runs.
- The targeted Behave contract passes.

# Evidence to Capture

- RED command and missing-text failure.
- GREEN command and pass summary.
