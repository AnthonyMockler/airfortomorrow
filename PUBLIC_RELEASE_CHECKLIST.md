# Public Release Checklist

## Preflight Scope

1. Validate all branches and tags intended for publication.
2. Confirm release branch state is aligned with approved hardening units.

## Secrets and Sensitive Data

1. Scan current tree for high-confidence secret patterns.
2. Scan full history for secrets and sensitive identity traces.
3. Confirm no `.env` or credentials are committed.
4. Confirm no logs expose usernames, tokens, or local machine paths.

## Code Security

1. No risky `eval` usage in release scripts.
2. No unsafe dynamic `shell=True` subprocess usage in Python wrappers.
3. Credential flow uses runtime environment variables only.
4. No plaintext password pass-through in wrappers.

## Repository Hygiene

1. No tracked `__pycache__/` or `*.pyc` artifacts.
2. Notebook policy enforced (curated set, output-stripped).
3. Large data files follow Git LFS policy.
4. Documentation is public-safe and does not include private access patterns.

## Documentation and Governance

1. `README.md` has public clone/setup instructions.
2. `SECURITY.md` exists with reporting path.
3. `CONTRIBUTING.md` exists with contribution and hygiene rules.
4. Model card and README are consistent on scope and limitations.

## Release Controls

1. CI security and dependency checks pass.
2. Final verification scans pass before publish.
3. Backup/mirror exists before any history rewrite.
4. Collaborator communication prepared for any forced-history updates.
