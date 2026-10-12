# Tasks: Generación de historia alternativa

**Input**: Design documents from `specs/001-historia-alternativa/`

**Prerequisites**: `plan.md`, `spec.md`; supporting decisions in `research.md`, `data-model.md`,
`contracts/procesar.yaml` and `quickstart.md`.

**Tests**: Required by the project constitution. Routine tests must mock Clerk and OpenRouter; no
automated test may contact either service. A real Clerk sign-in/logout check is manual.

**Organization**: Tasks are grouped by the three user stories from `spec.md`. Foundational Clerk
verification and test doubles unblock the API story; the visual Clerk flow is delivered as US2.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because files are distinct and there is no unfinished dependency.
- **[Story]**: User story mapping: US1 generation, US2 Clerk access/logout, US3 controlled errors.
- Every task names the concrete file(s) it creates or changes.

## Phase 1: Setup

**Purpose**: Establish the two application roots and reproducible local tooling.

- [ ] T001 Create the planned `backend/app/`, `backend/app/providers/`, `backend/app/services/`, `backend/tests/unit/`, `backend/tests/integration/`, `backend/api/`, `frontend/src/components/`, `frontend/src/services/`, `frontend/tests/`, and `deploy/` directories
- [ ] T002 Define exact Python runtime and backend/dev dependencies in `backend/pyproject.toml`, resolve and commit `backend/uv.lock`
- [ ] T003 Define exact Node runtime and Vue/Vite/Tailwind/Clerk dependencies and scripts in `frontend/package.json`, `frontend/package-lock.json`, `frontend/vite.config.js`, and `frontend/index.html`
- [ ] T004 Add fictional environment templates in `backend/.env.example` and `frontend/.env.example`; exclude secrets, `.venv`, `node_modules`, and build output in `.gitignore` and `.dockerignore`

---

## Phase 2: Foundational

**Purpose**: Shared backend configuration, authentication enforcement and external-service test
boundaries. These tasks block story implementation.

- [ ] T005 Implement typed environment settings, 25,000 ms provider timeout, configured Clerk issuer/authorized parties, OpenRouter model, and configurable CORS origins in `backend/app/config.py`
- [ ] T006 Create the FastAPI application, CORS middleware, request-validation error translation, and dependency wiring in `backend/app/main.py`
- [ ] T007 Implement a mockable Clerk request adapter in `backend/app/auth.py`; validate signature/expiry with the official SDK, then enforce configured `iss` and authorized-party/audience claims before protected processing
- [ ] T008 Add reusable fake Clerk verifier and fake OpenRouter client fixtures in `backend/tests/conftest.py`; ensure test configuration never reads real credentials
- [ ] T009 [P] Test missing, invalid, expired, and wrong-issuer/party tokens return 401 before the fake provider is called in `backend/tests/integration/test_auth.py`

**Checkpoint**: A protected FastAPI test request can use a fake authorized identity; rejected
requests make zero provider calls.

---

## Phase 3: User Story 1 - Explorar una historia alternativa (Priority: P1)

**Goal**: An authorized request produces the current alternate-history narrative and consequences
through the single endpoint, with exactly one provider request.

**Independent Test**: Call `POST /api/procesar` with a fake authorized identity and valid request;
assert HTTP 200, exactly `narrative` and `consequences` in the response, and one fake provider call.

### Tests for User Story 1

- [ ] T010 [P] [US1] Test strict request boundaries in `backend/tests/unit/test_models.py`: trimmed `question` is 1-280 characters, 281 and whitespace-only are rejected; `year` is an integer from 0 through 3000 inclusive with no boolean/coercion acceptance; `unrealismLevel` is exactly `realista`, `ilusionante`, or `descerebrado`
- [ ] T011 [P] [US1] Test authorized success and invalid HTTP requests in `backend/tests/integration/test_scenario_api.py`: success has only `narrative` and `consequences`, 3-5 non-empty consequences, and exactly one provider call; invalid input returns 422 and zero provider calls

### Implementation for User Story 1

- [ ] T012 [US1] Define strict Pydantic request, scenario result, and provider-output models in `backend/app/models.py` using the exact constraints in `specs/001-historia-alternativa/data-model.md`
- [ ] T013 [US1] Isolate the official OpenRouter client in `backend/app/providers/openrouter.py`; request JSON output with a 25,000 ms timeout and `RetryConfig(strategy="none", ...)`, and expose one mockable async operation
- [ ] T014 [US1] Implement the Spanish prompt and scenario use case in `backend/app/services/scenario.py`; validate the provider result and discard fields outside `narrative` and `consequences`
- [ ] T015 [US1] Implement authenticated `POST /api/procesar` in `backend/app/main.py`, composing request validation, auth dependency, scenario service, and success response without storing request/result data
- [ ] T016 [US1] Implement the single-endpoint JSON client in `frontend/src/services/api.js`; send the supplied Bearer token and typed request, and return only the successful `narrative` and `consequences`
- [ ] T017 [P] [US1] Implement question/year/level inputs and frontend validation in `frontend/src/components/HypothesisForm.vue`, mirroring the documented limits without replacing backend validation
- [ ] T018 [P] [US1] Render narrative and consequence strings as text in `frontend/src/components/ScenarioResult.vue`; do not interpret generated output as HTML
- [ ] T019 [US1] Compose the one-screen form and current result in `frontend/src/App.vue`; replace the previous result after a successful new request and keep all state in memory only

**Checkpoint**: With an authorized fake identity and fake provider, the endpoint and same-screen
scenario flow work; the success path calls the provider once.

---

## Phase 4: User Story 2 - Acceder con Clerk (Priority: P1)

**Goal**: The single screen offers Clerk sign-in and sign-out, and obtains a Bearer token for the
protected processing request without adding routes or application-owned accounts.

**Independent Test**: Automated backend tests use the fake verifier/provider to prove invalid or
absent tokens return 401 before AI. Manually verify inline Clerk access, Bearer submission, and
logout returning to the access state; the real Clerk check remains outside routine tests.

### Implementation for User Story 2

- [ ] T020 [US2] Initialize `@clerk/vue` with `VITE_CLERK_PUBLISHABLE_KEY` in `frontend/src/main.js`; keep secret Clerk/OpenRouter settings out of the frontend bundle
- [ ] T021 [US2] Implement inline `<SignIn routing="hash">` and an in-screen Clerk sign-out action in `frontend/src/components/ClerkAccess.vue`; do not add vue-router, a modal, or profile screens
- [ ] T022 [US2] Use Clerk `useAuth().getToken()` in `frontend/src/App.vue` and pass the current token to `frontend/src/services/api.js`; disable processing without a session and return the view to access state after logout
- [ ] T023 [US2] Add a manual verification checklist for real Clerk sign-in/logout and post-logout 401/no-provider-call behavior in `docs/validacion-manual.md`

**Checkpoint**: Clerk access and logout stay on the single screen; the backend remains the
authority and rejects requests without a valid token.

---

## Phase 5: User Story 3 - Entender y recuperarse de errores (Priority: P2)

**Goal**: Invalid requests, provider failures, unusable provider output and timeouts produce stable
Spanish errors without leaking internal or sensitive data; pending submissions cannot duplicate.

**Independent Test**: Simulate invalid input, provider exception, timeout, empty/malformed output,
and repeated submit; assert 422/502/504 as specified, zero provider calls for invalid input, no
second call while pending, and no internal/provider details in returned errors.

### Tests for User Story 3

- [ ] T024 [P] [US3] Test provider exception, timeout, empty output, malformed output, and consequences outside 3-5 items in `backend/tests/integration/test_scenario_errors.py`; assert 502/504 and safe error bodies
- [ ] T025 [P] [US3] Test duplicate-submit blocking, loading/error states, clearing stale output as required, and Spanish visible messages in `frontend/tests/scenario-flow.manual.md`

### Implementation for User Story 3

- [ ] T026 [US3] Map provider failures and unusable output to HTTP 502 and timeout to HTTP 504 in `backend/app/main.py`; return only `{"error":{"code":"...","message":"..."}}` in Spanish
- [ ] T027 [US3] Handle 401/422/502/504 and network failures in `frontend/src/services/api.js` and `frontend/src/App.vue`; display safe Spanish messages and never surface tokens, provider bodies, traces, or submitted text
- [ ] T028 [US3] Disable submit while processing, prevent duplicate requests, and clear/replace the current result consistently in `frontend/src/App.vue`

**Checkpoint**: Simulated failure cases map to the stable contract; pending UI blocks a second
provider request and the user can correct input or retry after completion.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the agreed quickstart and deployment packaging without performing real
deployments.

- [ ] T029 [P] Add the Vercel FastAPI function entrypoint in `backend/api/index.py` and deployment instructions in `docs/despliegue.md`; document locked `uv export --frozen --no-dev --no-emit-project -o requirements.txt` and verify no secret enters the frontend build
- [ ] T030 [P] Add the frontend/backend Docker Compose services and same-origin `/api` proxy in `deploy/docker-compose.yml` and `deploy/proxy.conf`; inject secrets only at runtime and define no persistent data volume
- [ ] T031 Update `README.md` and `specs/001-historia-alternativa/quickstart.md` with the verified local commands, environment-variable names, mock-only test policy, and separate Vercel/Docker paths
- [ ] T032 Record the actual Fase 5 AI assistance and human review decision in `docs/uso-ia.md`; keep “Comprobación humana” empty until the user records their review
- [ ] T033 Run backend tests, frontend production build, and the documented no-persistence/no-secret audit; record actual results in `docs/validacion.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: starts immediately; creates manifests and directories required by all work.
- **Foundational (Phase 2)**: depends on Setup; blocks all stories because it establishes settings,
  Clerk verification, application wiring and fake-service boundaries.
- **US1 (Phase 3)**: depends on Foundational; delivers the generation contract and screen with a
  fake authorized identity/provider for independent testing.
- **US2 (Phase 4)**: depends on Foundational and the US1 screen/API boundaries; integrates real
  Clerk client behavior. US1 backend tests do not require this UI integration.
- **US3 (Phase 5)**: depends on the provider and API path from US1; adds controlled failures and
  duplicate-submit behavior.
- **Polish (Phase 6)**: depends on all required stories and their focused checks.

### User Story Dependencies

- **US1 (P1)**: starts after Foundational; its API test uses the fake authorized identity fixture,
  not a real Clerk session.
- **US2 (P1)**: starts after Foundational; the frontend token handoff composes with the US1 API
  client. Its UI integration follows the US1 screen shell.
- **US3 (P2)**: starts after US1 provider/endpoint tasks; error rendering also composes with the
  US1 screen and US2 authenticated request path.

### Within Each User Story

- Tests precede the implementation they constrain.
- Models precede provider/service use; provider/service precede endpoint composition.
- Frontend components can be built in parallel only when they are in distinct files and do not
  require the unfinished parent-screen integration.
- Each story checkpoint must pass with fake service boundaries before moving to the next phase.

## Parallel Opportunities

- **Setup**: T002, T003, and T004 can proceed in parallel after T001 establishes directories.
- **Foundational**: T007 and T008 can proceed in parallel after T005; T009 follows both the auth
  adapter and fake verifier fixture.
- **US1 tests/UI**: T010, T011, T017, and T018 touch separate files and can proceed in parallel
  after Setup/Foundational; T012-T015 remain ordered backend dependencies.
- **US2**: T020 and T023 can proceed independently; T021 follows T020; T022 follows T016, T019,
  and T021.
- **US3**: T024 and T025 can proceed in parallel; T026 and T027 follow their corresponding tests.
- **Polish**: T029 and T030 can proceed in parallel; T031-T033 follow relevant implementation and
  verification work.

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational.
2. Complete US1 backend models/provider/service/endpoint with mocked Clerk and OpenRouter.
3. Validate request boundaries and exactly one provider call, then complete the US1 screen.
4. Add US2 Clerk sign-in/logout and verify manually with a real Clerk development project.
5. Add US3 controlled errors, then deployment/docs polish.

### Incremental Delivery

Each story is verified at its checkpoint. No phase implies a real service call or deployment; actual
Vercel/AWS deployments remain the user's action.

## Notes

- `[P]` means distinct files and no dependency on unfinished tasks; story tasks always include the
  matching `[US1]`, `[US2]`, or `[US3]` label.
- Every task names at least one exact repository path and is unchecked until implemented.
- Tests call only fake Clerk/provider boundaries. Clerk's real login/logout check is manual.
- `docs/validacion.md` records only commands actually run; do not claim pre-implementation checks
  as product test results.