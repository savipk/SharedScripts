### Best practices for unit tests (in this repo)

- **Scope**: Unit tests live in `tests/unit/` and should target domain logic (`mapper_api/domain/**`) and application logic that can be isolated. They must not hit external services.
- **Isolation**: Use `mock/` components (e.g., `mock/llm_client.py`, `mock/definitions_repo.py`) and dependency injection so tests are fast, deterministic, and framework-free (aligns with Clean Architecture).
- **Speed**: Keep unit tests <100ms each where possible. No network, I/O, or Azure calls.
- **Naming/structure**: `tests/unit/test_*.py`, functions `test_*`, one behavior per test, clear Arrange-Act-Assert.
- **Coverage**: Track coverage for `mapper_api/` and enforce a threshold for merges.
- **Determinism**: No time-based sleeps, random without seeding, or order dependencies.

### Which tests run after code changes

- **Locally (developer)**:
  - Quick loop: run only affected or nearby unit tests first.
  - Before pushing: run the entire `tests/unit/` suite.
- **CI (on every PR commit)**:
  - Always run the full `tests/unit/` suite.
  - Optionally shard/parallelize to keep it fast.
- **On `main` merges / nightly**:
  - Full `tests/unit/` and then slower `tests/integration/` in a separate job.

### How to run

- **All unit tests**
```bash
cd /Users/savikuriakose/projects/mapper-api
pytest -q tests/unit
```

- **A specific file or test**
```bash
pytest -q tests/unit/test_use_cases.py
pytest -q tests/unit/test_use_cases.py::test_map_control_to_5ws
```

- **Filter by keyword**
```bash
pytest -q tests/unit -k fivews
```

- **Coverage (recommended locally and in CI)**
```bash
pytest tests/unit --cov=mapper_api --cov-report=term-missing --cov-fail-under=90
```

- **Faster feedback options (optional plugins)**
  - Only tests impacted by changes: `pytest -q --testmon` (pytest-testmon) or `pytest-picked -k` for changed files.
  - Parallel: `pytest -q -n auto` (pytest-xdist).
  - Only re-run last failures: `pytest -q --last-failed --maxfail=1`.

- **Watch mode (optional)**
```bash
ptw tests/unit  # via pytest-watch
```

### When and by whom

- **Developer (local)**
  - On each change: run nearby/affected unit tests for fast iteration.
  - Before commit/push: run `tests/unit/` fully; fix failures and keep coverage ≥ threshold.

- **CI (automation/bot)**
  - On every PR update: run full `tests/unit/` with coverage and fail the check if tests fail or coverage < threshold.
  - On merge to `main`: run full `tests/unit/`; optionally trigger `tests/integration/`.

- **Maintainers/Release**
  - Gate merges on passing CI checks.
  - Periodic or pre-release: run `tests/integration/` and any smoke tests.

### Repo-specific guidance

- **Clean Architecture**: Unit tests target `domain/**` and pure application services; avoid touching infrastructure. Use DI to provide fakes from `mock/`.
- **External boundaries**: Anything with Azure OpenAI or Blob should be mocked in unit tests; real calls belong only in `tests/integration/`.
- **No hot reload**: Tests should not assume dynamic reload of definitions; setup test fixtures to load once per session if needed.

### Minimal CI matrix (example)

- **PR job (fast)**: `pytest tests/unit --cov=mapper_api --cov-fail-under=90`
- **Main job**: same as PR; then trigger integration job
- **Nightly (optional)**: `pytest tests/integration`

### Quick local recipes

- **Fast sanity loop**
```bash
pytest -q tests/unit --maxfail=1 -x
```

- **Changed files only (if plugin installed)**
```bash
pytest -q --picked
```

- **Target the code you’re changing**
```bash
pytest -q tests/unit -k map_control_to_5ws
```

- **Parallel + coverage**
```bash
pytest -q -n auto tests/unit --cov=mapper_api --cov-fail-under=90
```

- **Integration (only when needed)**
```bash
pytest -q tests/integration
```

- **Pre-push hook idea**
```bash
pytest -q tests/unit --cov=mapper_api --cov-fail-under=90 || exit 1
```

- **What to run after your edit?**
  - Immediate: closest test file(s) in `tests/unit/` plus any focused tests.
  - Before push: entire `tests/unit/`.

- **Who runs what**
  - Developer: focused + full unit suite.
  - CI: full `tests/unit/` on PR; integration on main/nightly.

- Keep unit tests fast, isolated, and stable; push integration concerns to `tests/integration`.

- Unit tests live in `tests/unit/`; they run locally before push and in CI on every PR. Integration tests live in `tests/integration/`; they run on main or nightly. For quick loops, run affected tests; before push and in CI, run all of `tests/unit/` with coverage and mocks for external boundaries.
