# Decision

Add a dedicated fast static-asset contract path that validates the CSV bootstrap assets against the loader assumptions used by the AQ pipeline, instead of relying only on checksum validation and slow end-to-end workflows.

# Why

The current suite protects bootstrap assets in two indirect ways: `scripts/setup.sh` verifies presence and checksums, and slower live workflow scenarios eventually exercise some of the downstream readers. That leaves a gap for format-change work on the large CSV assets because the fast path does not prove loader compatibility, while the comprehensive path is too slow and broad for regular iteration.

# Change Scope

- Add a focused validator entrypoint for static/bootstrap CSV assets used by silver generation and historical FIRMS ingestion.
- Add Behave contract coverage for that validator so the repo has a regular fast path for asset-format changes.
- Keep the existing checksum-based setup validation in place as a separate integrity guard.
- Document the new fast-path tag/command in test guidance.

# Non-Goals

- Do not change the production asset formats yet.
- Do not remove checksum validation from `scripts/setup.sh`.
- Do not replace the existing live or slow workflow scenarios.
