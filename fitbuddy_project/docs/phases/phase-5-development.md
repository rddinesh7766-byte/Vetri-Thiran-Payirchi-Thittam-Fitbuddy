# Phase 5 – Project Development

The complete implementation is in the repository root. Core behavior:

- `/generate-workout` saves the user, generates a plan and stores it.
- `/submit-feedback` loads the active plan, revises it and stores the updated version.
- `/view-all-users` displays all stored users/plans.
- `/api/plans` and `/api/plans/{user_id}/feedback` provide JSON interfaces.
- `DEMO_MODE=true` provides an offline deterministic AI simulation for development and testing.
