# Gold Labels And Training Reference

- Status: Reference detail for slice 1 and later phases
- Date: 2026-03-18
- Scope: Preserve the current gold-label and training-policy decisions without crowding the core architecture spec.

## Gold Labels

- Training labels may live inside `gold.model_features` in v1.
- For v1, keep labels aligned to the same `date_utc = D` inside `gold.model_features`.
- If training needs `D -> D+1` shifting, do that in training code for now.
- Revisit later whether label shifting should move from training code into the gold build itself.

## Training, Eval, And Inference

- For v1, training should use predominantly reference-grade rows.
- Eval and test should use reference-grade rows.
- Inference should score every row in the dense gold grid.
- Keep the training reference-dominance threshold configurable rather than hardcoding it into the architecture.
