### Architecture overview (Clean Architecture)

- **Domain layer (core business)**
  - Location: `mapper_api/domain/`
  - Contents: `entities/`, `value_objects/`, `repositories/` (ports), `services/`, `errors.py`
  - Characteristics:
    - Framework‑free, pure Python. No Pydantic.
    - Enforces invariants and raises domain exceptions (`DomainError`, `ValidationError`, `DefinitionsNotLoadedError`).
    - Example: `entities/control.py`, `value_objects/score.py`, `repositories/definitions.py` (port interface).

- **Application layer (use cases)**
  - Location: `mapper_api/application/`
  - Contents: `use_cases/`, `prompts/`, `mappers/` (assemblers), `dto/` (Pydantic models for boundaries), `ports/` (LLM client port)
  - Responsibilities:
    - Orchestrates domain logic and external calls via ports.
    - Builds LLM prompts, validates strict JSON outputs with Pydantic v2.
    - Maps domain outputs to response DTO dicts.
  - Examples:
    - `use_cases/map_control_to_5ws.py`, `use_cases/map_control_to_themes.py`
    - `dto/output_schemas.py` (strict LLM schemas), `dto/responses.py` (HTTP DTOs)
    - `ports/llm.py` (LLM port), `mappers/assemblers.py` (domain → DTO dict)

- **Infrastructure layer (adapters)**
  - Location: `mapper_api/infrastructure/`
  - Contents: `azure/` (OpenAI client, Blob repo), `logging/`
  - Responsibilities:
    - Implements application/domain ports using real services (Azure OpenAI, Azure Blob).
    - Follows rule: definitions loaded once at startup (no hot reload).
  - Examples: `azure/openai_client.py`, `azure/blob_definitions_repo.py`

- **Interface layer (delivery/HTTP)**
  - Location: `mapper_api/interface/http/`
  - Contents: `api.py`, `routers/`, `errors.py`, `state.py`
  - Responsibilities:
    - FastAPI endpoints, request/response handling.
    - Registers exception handlers mapping domain errors to HTTP codes.
    - Uses DI to obtain use cases and adapters.
  - Examples:
    - Routers: `routers/fivews_mapper.py`, `routers/taxonomy_mapper.py`
    - Error mapping: `errors.py` (400 for `ValidationError`, 404 for `DefinitionsNotLoadedError`, 500 fallback)
    - App wiring: `api.py` (versioned routes, handlers)

- **Configuration and DI**
  - Location: `mapper_api/config/`, `mapper_api/interface/di/`
  - Responsibilities:
    - `config/settings.py` centralizes settings (e.g., API version, Azure config).
    - DI containers wire ports to infrastructure or mocks: `di/container.py`, `di/mock_container.py`.

- **Mocks for testing/offline**
  - Location: `mapper_api/mock/`
  - Responsibilities:
    - Test doubles for ports (mock LLM client, in‑memory definitions repo).
  - Examples: `mock/llm_client.py`, `mock/definitions_repo.py`.

### Data flow

- HTTP request → router (`interface/http/routers`) → use case (`application/use_cases`) → domain validation/entities → LLM via port (`application/ports.llm` implemented by `infrastructure/azure/openai_client.py`) with strict JSON schema → Pydantic v2 validation (`application/dto/output_schemas.py`) → map to response DTO dict (`application/mappers/assemblers.py`) → HTTP response.
- Errors raised in domain/application are translated to HTTP in `interface/http/errors.py`.

### Key project rules enforced

- **Clean Architecture**: Domain is independent of frameworks and infrastructure.
- **Pydantic only at boundaries**: DTOs for LLM validation and HTTP I/O; domain stays framework‑free.
- **Azure OpenAI strict JSON**: schema via `response_format.json_schema` with `strict=True`.
- **Definitions load-once**: Loaded from Azure Blob at startup; no hot reload.
- **API contracts exact**: Field names and shapes (e.g., `FiveWData.fivews` serialized as `"5ws"`) must match.
