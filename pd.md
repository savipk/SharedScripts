I'll scan how errors are defined in the domain and how they're translated at the HTTP layer, then summarize the conventions.

[5 tools called]

I'll check how exception handlers are registered in the HTTP layer to complete the documentation.

[1 tool called]

### Error handling overview

- Domain errors
  - Defined in `mapper_api/domain/errors.py`:
    - `DomainError` (base)
    - `ValidationError`: domain/validation failures
    - `DefinitionsNotLoadedError`: definitions missing
- Raising errors
  - Use cases raise domain errors:
    - Empty control text → `ValidationError`
    - Missing definitions → `DefinitionsNotLoadedError`
    - LLM schema/validation failures → `ValidationError`
- HTTP mapping
  - Handlers in `mapper_api/interface/http/errors.py`:
    - `ValidationError` and FastAPI `RequestValidationError` → 400 with `{"error", "traceId"}`
    - `DefinitionsNotLoadedError` → 404 with `{"error", "traceId"}`
    - Any other `Exception` → 500 with `{"error": "Internal Server Error", "traceId"}`
  - Registered in `mapper_api/interface/http/api.py` via `app.add_exception_handler(...)`
- Router usage
  - Routers pre-check definitions and raise `DefinitionsNotLoadedError` if not loaded.

### Conventions

- Raise domain-specific exceptions from domain/use-case layers.
- Do not return HTTP responses from domain/application layers.
- Include a meaningful message in exceptions; it is surfaced as `"error"` in responses.
- `traceId` is sourced from `x-trace-id` header for all error responses.

### Quick examples

- Domain:
```python
if not ctrl.text.strip():
    raise ValidationError("controlDescription must not be empty")
```

- HTTP response mapping:
- Validation failure → 400
- Definitions missing → 404
- Unexpected error → 500

This keeps the domain clean (framework-free) and centralizes HTTP concerns in the interface layer.
