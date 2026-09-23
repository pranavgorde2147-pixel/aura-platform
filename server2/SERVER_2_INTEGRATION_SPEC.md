# AURA Server 1 → Server 2 Integration Specification

## Scope

This document defines the integration contract for the next stage of the architecture:

- Server 1 remains the ecosystem, identity, auth, ownership, orchestration, and security boundary.
- The Personal Brain is the Tiny LLM runtime, specifically Qwen3.5-4B, running on Server 2.
- Server 2 is not a user database, not a vault, not a general-purpose app server, and not a replacement for the Personal Brain.
- Server 3 remains future personal vault/storage work and is explicitly out of scope here.

This spec is intentionally constrained to the current project state and the authoritative architecture already present in the Server 1 implementation:

- Applications are doors only.
- The Personal Brain is the mandatory intelligence boundary.
- The Personal Brain is conceptually a dedicated tiny LLM for a single user.
- The Personal Vault belongs to that user and is accessed through the Brain boundary.
- Server 1 provides the platform and boundary logic.
- Server 2 provides the actual Tiny LLM inference runtime.

---

## 1. SERVER 1 → SERVER 2 ARCHITECTURE

### 1.1 Canonical architecture

```text
APPS
  ↓
SERVER 1 / ECOSYSTEM
  - auth
  - user ownership
  - governance
  - request validation
  - orchestration
  - context preparation
  - Personal Brain boundary
  ↓
PERSONAL BRAIN
  = Qwen3.5-4B running on Server 2
  ↓
SERVER 2 TINY LLM INFERENCE RUNTIME
  - load model
  - run inference
  - return generated answer
```

### 1.2 Exact request flow

1. A client app authenticates with Server 1.
2. Server 1 resolves the current authenticated user via the existing `get_current_user` dependency and enforced ownership rules.
3. The app calls the Server 1 Brain API, currently represented by:
   - `POST /api/v1/brain/query`
   - `POST /api/v1/brain/ingest`
4. Server 1 creates a `PersonalBrainService` instance and calls its orchestration logic.
5. Server 1 calls the internal provider abstraction path represented in `backend/app/services/brain_provider.py` and `backend/app/services/personal_brain.py`.
6. Server 1 prepares a minimal, privacy-safe context package using the existing `prepare_external_context()` pattern.
7. Server 1 sends only approved context to Server 2.
8. Server 2 loads Qwen3.5-4B and runs inference on the incoming prompt.
9. Server 2 returns the generated response to Server 1.
10. Server 1 wraps or personalizes the result and returns the final answer to the app.

### 1.3 Exact response flow

1. Server 2 receives a request from Server 1.
2. Server 2 validates authentication, schema, and model readiness.
3. Server 2 runs the exact model Qwen3.5-4B.
4. Server 2 returns a JSON response to Server 1.
5. Server 1 stores the response in the orchestration layer and returns the final app-facing result.
6. Server 1 never exposes direct access to the model runtime to applications.

### 1.4 What Server 1 sends to Server 2

Server 1 does not send the user vault, raw database records, or unrelated user data. Server 1 sends a minimal request built from the current architecture contract:

```json
{
  "user_id": "<uuid>",
  "query": "<user prompt>",
  "context": {
    "user_level": "general",
    "relevant_context": {
      "schedule": "busy",
      "known_topics": ["sql"],
      "goals": ["improve study plan"]
    },
    "safety_constraints": [
      "never_forward_full_vault",
      "only_send_minimal_context"
    ]
  },
  "request_id": "<uuid>",
  "model": "Qwen3.5-4B"
}
```

This aligns with the current code in `backend/app/services/personal_brain.py`, where `prepare_external_context()` explicitly strips or minimizes context and avoids forwarding the full vault.

### 1.5 What Server 2 returns

Server 2 returns only the model result and metadata required for orchestration:

```json
{
  "model": "Qwen3.5-4B",
  "response": "<generated answer>",
  "user_id": "<uuid>",
  "request_id": "<uuid>",
  "status": "ok",
  "tokens_used": 0,
  "latency_ms": 0
}
```

### 1.6 Responsibility ownership

| Component | Responsibility |
| --- | --- |
| Server 1 / app layer | Auth, ownership, request routing, context filtering, orchestration, API contracts |
| Personal Brain boundary | The user-specific intelligence boundary; in this project it is the Qwen3.5-4B runtime on Server 2 |
| Server 2 | Model loading, inference runtime, request validation, Qwen3.5-4B execution |
| Server 3 | Future personal vault/storage system; explicitly not implemented here |

---

## 2. BRAIN / LLM RESPONSIBILITY

### 2.1 Final role definition

This project is not building a fake rule-based brain in Server 1 that is meant to replace the model. The architecture is explicit:

- Server 1 = ecosystem and security boundary
- Personal Brain = the actual Tiny LLM intelligence boundary
- Server 2 = the runtime that executes the Tiny LLM
- Server 3 = future storage-vault layer

### 2.2 What is the Personal Brain?

The Personal Brain is the Qwen3.5-4B model deployed on Server 2.

It is not:

- a CRUD object for memory records
- a fake data router
- a custom rule engine replacing the model
- a vault or database
- a user-data storage layer

### 2.3 What is Server 1 responsible for?

Server 1 owns:

- user authentication and JWT handling
- current-user dependency enforcement
- user ownership checks and cross-user isolation
- API boundary for `/api/v1/brain/*`
- orchestration of the user request
- context preparation and minimal privacy filtering
- identifying whether a request is valid for the model boundary
- returning a final response to the app

This is already reflected in:

- `backend/app/api/v1/brain.py`
- `backend/app/services/personal_brain.py`
- `backend/app/services/brain_provider.py`
- `backend/app/schemas/brain.py`

### 2.4 What is Server 2 responsible for?

Server 2 owns:

- hosting the model
- receiving a prepared inference request from Server 1
- validating auth/token
- running Qwen3.5-4B
- returning the model response
- exposing a health endpoint

### 2.5 What is Server 3 responsible for?

Future Server 3 owns:

- personal vault storage
- persistent memory store
- broader personal data lifecycle
- long-term retrieval patterns

It must not exist in the current Server 2 implementation.

---

## 3. API CONTRACT

### 3.1 Contract choice

The current Server 1 code does not yet implement a concrete remote model client. However, the existing architecture strongly suggests a simple internal inference API with a minimal service-level contract. The most appropriate contract is:

- `POST /v1/brain/infer`
- `GET /health`

This matches the project direction of a simple internal Server 2 runtime and is consistent with the idea that Server 1 should not expose model access to applications directly.

### 3.2 Method and endpoints

#### POST /v1/brain/infer

Purpose: Execute a prepared user query against the Qwen3.5-4B Personal Brain model.

#### GET /health

Purpose: Return liveness/readiness for Docker health checks and Server 1 connection verification.

### 3.3 Request JSON schema

```json
{
  "user_id": "string (UUID)",
  "query": "string (required)",
  "context": {
    "user_level": "string (optional)",
    "relevant_context": "object (optional)",
    "safety_constraints": ["string"]
  },
  "request_id": "string (UUID, optional but recommended)",
  "model": "Qwen3.5-4B"
}
```

Validation rules:

- `user_id` must be a valid UUID
- `query` must be non-empty
- `context.relevant_context` must not include raw vault payloads or full storage blocks
- `model` must equal `Qwen3.5-4B`

### 3.4 Response JSON schema

```json
{
  "model": "Qwen3.5-4B",
  "response": "string",
  "user_id": "string (UUID)",
  "request_id": "string (UUID)",
  "status": "ok",
  "tokens_used": 0,
  "latency_ms": 0
}
```

### 3.5 Authentication mechanism

Server 2 should not be public. It should require an internal bearer token:

```http
Authorization: Bearer <SERVER2_INTERNAL_TOKEN>
```

This is the recommended pattern because Server 1 already uses JWT for user auth, and the model runtime should enforce an internal service-only secret.

Server 1 should set this value in environment variables and not hardcode it.

### 3.6 Error responses

Recommended behavior:

- `401 Unauthorized` — missing or invalid internal token
- `403 Forbidden` — token valid but not allowed for model gateway
- `422 Unprocessable Entity` — malformed request payload
- `429 Too Many Requests` — rate-limited
- `500 Internal Server Error` — model loader/runtime failure

Example error JSON:

```json
{
  "error": "invalid_auth",
  "message": "Server 2 internal token is missing or invalid"
}
```

### 3.7 Timeout expectations

Recommended timeout budget:

- model request timeout: 30s to 90s for normal prompt generation
- if the prompt is long or the model is busy, 120s is acceptable in development only
- Server 1 should treat model latency as an external service dependency and time out cleanly rather than hanging requests

### 3.8 Health endpoint

```json
{
  "status": "ok",
  "model": "Qwen3.5-4B",
  "version": "<model revision>",
  "uptime_seconds": 123
}
```

`GET /health` should be used by Docker healthchecks and by Server 1 connection validation.

---

## 4. NETWORKING

### 4.1 Correct network topology

Server 2 should be deployed on a private internal network, not the public internet.

Recommended model:

- Same laptop in development: localhost or Docker internal network
- Same Docker Compose project: internal Docker network
- Remote machine: private LAN or VPN, not public internet
- Production: internal private network / trusted subnet / reverse proxy only

### 4.2 Recommended development setup on this laptop

Because the current Server 1 config already defaults to `AI_SERVER_URL=http://localhost:8001` in `backend/app/core/config.py`, the default development approach should be:

- Server 2 listens on port `8001`
- Server 1 runs locally and points to `http://localhost:8001`
- If Server 1 is also running in Docker, it should point to `http://host.docker.internal:8001` or to a Docker service name, depending on the Compose topology

This is the most likely correct setup for this machine.

### 4.3 Recommended production setup

- Server 2 should not be publicly exposed.
- Run it on a private internal Docker network or private host.
- Server 1 should connect over the private network only.
- If there is a load balancer or reverse proxy, it should be restricted to trusted internal clients only.

### 4.4 Host/IP configuration

The host/hostname should be configured in environment variables, not hardcoded in code.

The existing Server 1 config already includes:

- `AI_SERVER_URL` in `backend/app/core/config.py`

This is the correct place to configure the Server 2 endpoint for Server 1.

Recommended values:

- Development, same machine: `http://localhost:8001`
- Development, Server 1 in Docker: `http://host.docker.internal:8001`
- Internal compose network: `http://aura-server2:8001`
- LAN/shared workstation: `http://<server2-host>:8001`

Do not invent a fixed IP address in the integration design.

### 4.5 Port

Use port `8001` as the default internal model service port.

This matches the current Server 1 default `AI_SERVER_URL` value already present in the code.

### 4.6 Environment variables

Server 1 should define:

```bash
AI_SERVER_URL=http://localhost:8001
AI_SERVER_INTERNAL_TOKEN=replace-with-shared-secret
AI_BRAIN_MODEL=Qwen3.5-4B
AI_BRAIN_TIMEOUT_MS=30000
```

Server 2 should define:

```bash
HOST=0.0.0.0
PORT=8001
MODEL_NAME=Qwen3.5-4B
MODEL_PATH=/models/Qwen3.5-4B
INTERNAL_API_TOKEN=replace-with-shared-secret
```

### 4.7 CORS requirements

CORS is not required for direct service-to-service internal API traffic.

If a browser will ever access Server 2 directly, extremely restrictive CORS should be enabled, but that is not the intended architecture. The direct path is Server 1 → Server 2, not browser → Server 2.

### 4.8 Firewall requirements

- Allow only Server 1 to connect to Server 2.
- Block public inbound access to port `8001` unless a trusted internal network explicitly requires it.
- If on a LAN, restrict the port to the Server 1 host or subnet.

---

## 5. DOCKER REQUIREMENTS

### 5.1 Dockerization requirement

Server 2 must be Dockerized. The design should be a single-model inference service that runs the Qwen3.5-4B runtime and exposes only the internal inference API and health endpoint.

### 5.2 Dockerfile requirements

The Dockerfile should:

- use a Python base image or CUDA-enabled base image
- install the model runtime dependencies
- copy the application code
- mount the downloaded model directory
- expose port `8001`
- run a small FastAPI or ASGI service
- set the model path environment variable
- include a healthcheck on `GET /health`

Recommended base choice:

- CPU/dev laptop: Python base image with PyTorch/Transformers
- GPU-capable host: NVIDIA CUDA base image for improved performance

### 5.3 Docker Compose requirements

Recommended minimal Compose structure:

```yaml
services:
  aura-server2:
    build:
      context: ./server2
    container_name: aura-server2
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      HOST: 0.0.0.0
      PORT: 8001
      MODEL_NAME: Qwen3.5-4B
      MODEL_PATH: /models/Qwen3.5-4B
      INTERNAL_API_TOKEN: ${AI_SERVER_INTERNAL_TOKEN}
    volumes:
      - /home/pranav_gorde/aura/server2/models/Qwen3.5-4B:/models/Qwen3.5-4B:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
```

### 5.4 Model volume and mount

The exact model directory already exists locally:

```text
/home/pranav_gorde/aura/server2/models/Qwen3.5-4B
```

Recommended mount inside the container:

```text
/models/Qwen3.5-4B
```

This is the correct target for a read-only model mount.

### 5.5 Exposed port

- Host/container expose: `8001:8001`
- Internal server: `PORT=8001`

This matches the existing Server 1 default and keeps the platform consistent with the current code.

### 5.6 Environment variables

Server 2 environment required:

```bash
HOST=0.0.0.0
PORT=8001
MODEL_NAME=Qwen3.5-4B
MODEL_PATH=/models/Qwen3.5-4B
INTERNAL_API_TOKEN=replace-with-shared-secret
```

Optional runtime tuning:

```bash
MAX_NEW_TOKENS=512
TEMPERATURE=0.2
GPU_ENABLED=false
```

### 5.7 CPU/GPU considerations

Current laptop environment should be assumed to be CPU-first unless otherwise confirmed. For this exact model and this project stage:

- CPU-only is acceptable for development and validation
- GPU is strongly preferred for faster response times and lower latency
- If the laptop has NVIDIA CUDA, enable GPU in Docker Compose with `nvidia-container-toolkit`
- If no GPU is available, keep the model in CPU mode and make the request timeouts realistic

### 5.8 Healthcheck

Server 2 should provide `GET /health` and the container should run a healthcheck against it.

Recommended healthcheck behavior:

- `200 OK` means service is ready
- failure should trigger restart policy if configured

### 5.9 Restart policy

Recommended:

```yaml
restart: unless-stopped
```

This gives the service resilience without creating unsafe restart loops.

### 5.10 How Server 1 reaches the container

Server 1 reaches the container using environment configuration, not hardcoded paths:

- same machine native Server 1: `http://localhost:8001`
- same Compose network: `http://aura-server2:8001`
- server-host connection: `http://<server2-host>:8001`

The important rule: Server 1 must never reach a model by directly reading files from the local model directory. It must use the HTTP inference API.

---

## 6. MODEL REQUIREMENTS

### 6.1 Exact model commitment

The exact model to be served is:

- Qwen3.5-4B

This is the project’s committed Tiny LLM for the Personal Brain.

No alternate model should be introduced in this phase.

### 6.2 Exact local model path

The local downloaded model directory exists here:

```text
/home/pranav_gorde/aura/server2/models/Qwen3.5-4B
```

This directory contains the model payload, tokenizers, and config files. Server 2 should mount this directory read-only and point the runtime to:

```text
MODEL_PATH=/models/Qwen3.5-4B
```

### 6.3 What not to do

- Do not download another model
- Do not replace the model
- Do not choose a different architecture
- Do not add generalized LLMs to this server yet

---

## 7. INFERENCE RUNTIME

### 7.1 Recommended runtime/framework

For this exact model and current project state, the recommended runtime is:

- Hugging Face `transformers` + `torch`
- served via a small FastAPI app

This is the safest and most appropriate choice for this project because:

- the model is already downloaded locally
- the project does not yet have a generalized routing architecture
- the current architecture is a simple internal inference service
- Server 1 already expects a minimal provider boundary rather than a heavy inference platform
- it keeps the integration simple and testable on a single laptop

### 7.2 Why this is appropriate

The model is a standard local Hugging Face checkpoint and matches the architecture of a straightforward inference service. A simple FastAPI + Transformers container is easier to validate on the current laptop than a full prepared inference engine and does not require broad system configuration or additional model orchestration before the boundary is working.

### 7.3 Future upgrade path

If throughput or GPU efficiency becomes important later, the runtime can evolve to:

- vLLM for high-throughput inference
- model routing for multiple models
- more advanced batching

But those are future steps and are not part of this initial integration.

---

## 8. SECURITY

### 8.1 Should Server 2 be publicly exposed?

No. It should not be publicly exposed.

It should be treated as an internal inference service only.

### 8.2 How does Server 1 authenticate to Server 2?

By using a shared internal secret, ideally as a bearer token:

```http
Authorization: Bearer <SERVER2_INTERNAL_TOKEN>
```

This is the cleanest option because it leaves the user JWT flow in Server 1 untouched and creates a separate service-to-service trust boundary for model execution.

### 8.3 Does the model endpoint need an API key?

Yes, for internal use it should have a service-level token or shared secret. Server 2 should reject anonymous traffic.

### 8.4 What data is Server 2 allowed to receive?

Allowed payload data is limited to:

- a `user_id`
- an approved query
- a minimal context block prepared by Server 1
- a `request_id`
- the model name (`Qwen3.5-4B`)

The context must be explicitly filtered to safe, minimal, user-approved information.

### 8.5 What must Server 2 never independently access?

Server 2 must never directly access:

- the Personal Vault database
- the Server 1 database
- full user memory or knowledge graphs
- unrelated users’ personal data
- Server 3 storage
- any unfiltered vault payloads

What crosses the boundary is only what Server 1 intentionally prepares and approves.

---

## 9. DATA PRIVACY

### 9.1 Privacy rule

The Personal Brain boundary is the privacy gate.

Server 2 must never have direct access to the vault or raw user storage. This is not optional. The architecture explicitly requires the context-preparation step to filter information before it is transmitted.

### 9.2 What information is allowed to cross Server 1 → Server 2

Allowed cross-boundary information includes:

- the current user identifier
- the current prompt/query
- minimal user context relevant to the immediate request
- safety constraints and response policy hints
- non-sensitive user metadata required for personalization

Example permitted context:

```json
{
  "user_level": "intermediate",
  "relevant_context": {
    "schedule": "busy",
    "known_topics": ["sql"],
    "goals": ["improve study plan"]
  },
  "safety_constraints": [
    "never_forward_full_vault",
    "only_send_minimal_context"
  ]
}
```

### 9.3 What must never be sent to Server 2

Server 2 must never receive:

- raw vault dumps
- complete personal memory data
- server-side personal storage references
- unrelated users’ records
- any unfiltered database entities
- any direct Server 3 backend access

This responsibility remains in Server 1, via the Personal Brain service and the context preparation contract.

---

## 10. FUTURE EXPANSION

### 10.1 Design for future growth without implementing it now

Server 2 should be structured so that later it can support:

- generalized LLMs
- additional inference models
- model selection/routing
- multi-model endpoints
- model-specific health and load metrics

### 10.2 Current-only commitment

At this stage, Server 2 must support only:

- Qwen3.5-4B
- Personal Brain inference
- internal service API
- health endpoint

### 10.3 Future routing design

In a later architecture, the internal API could be extended with:

```json
{
  "model": "Qwen3.5-4B",
  "route": "personal_brain"
}
```

But that is not required now. For now, the model name is fixed to `Qwen3.5-4B`.

---

## 11. DEPLOYMENT / MIGRATION

### 11.1 What needs to be copied to another laptop

To replicate the setup on a friend’s machine, the following must be copied:

- Dockerfile for Server 2
- docker-compose file
- application code for the Server 2 service
- the model directory: `/home/pranav_gorde/aura/server2/models/Qwen3.5-4B`
- any `.env` file containing the internal auth token and runtime configuration

### 11.2 What model files need to be copied

The full local model directory should be copied or mounted as-is:

```text
/home/pranav_gorde/aura/server2/models/Qwen3.5-4B
```

This should be treated as a model artifact volume, not regenerated.

### 11.3 What the friend needs to install

The friend should install:

- Docker
- Docker Compose
- NVIDIA Container Toolkit if using GPU mode
- curl or another healthcheck tool if not installed by default

### 11.4 What environment variables need changing

The following values must be updated when moving machines:

- `AI_SERVER_URL` in Server 1
- `AI_SERVER_INTERNAL_TOKEN` in Server 1 and Server 2
- hostnames or service names in Compose or the environment file
- any model path if the model is stored in a different location

### 11.5 How Server 1 discovers/connects to Server 2 on another machine

Server 1 should use a config value that points to the other machine, for example:

```bash
AI_SERVER_URL=http://<server2-host>:8001
```

or, in Docker compose mode:

```bash
AI_SERVER_URL=http://aura-server2:8001
```

This should be fully environment-driven and must not be hardcoded into the code.

### 11.6 What must not be hardcoded

The following must never be hardcoded:

- endpoint host
- endpoint port
- model path
- internal auth token
- any user-specific vault access

---

## 12. EXACT BUILD CHECKLIST

### Server 2 build checklist

1. Confirm the model directory exists at:
   `/home/pranav_gorde/aura/server2/models/Qwen3.5-4B`
2. Create the Dockerized Server 2 service.
3. Set `MODEL_NAME=Qwen3.5-4B`.
4. Set `MODEL_PATH=/models/Qwen3.5-4B`.
5. Mount the model directory read-only into the container.
6. Expose port `8001`.
7. Implement `GET /health`.
8. Implement `POST /v1/brain/infer`.
9. Require internal auth token.
10. Keep the service private to Server 1.
11. Start the container.
12. Verify `/health` returns `200 OK`.
13. Verify the model loads correctly.
14. Verify Server 1 can reach the endpoint.
15. Run a small inference test.
16. Confirm only Qwen3.5-4B is loaded.
17. Confirm no direct vault or database access is present.
18. Freeze the design to this single model until later expansion.

---

## 13. ACCEPTANCE TESTS

The following tests prove that the integration is correct.

### 13.1 Docker starts

- Server 2 container starts successfully
- container remains healthy after startup
- no crash loop occurs during model load

### 13.2 Model loads

- model path resolves to `/models/Qwen3.5-4B`
- model config loads successfully
- tokenizer loads successfully
- no duplicate model variants are loaded

### 13.3 `/health` works

- `GET /health` returns `200 OK`
- response includes service status and model name
- health endpoint works before inference requests are sent

### 13.4 Server 1 can reach Server 2

- Server 1 sends a request to `http://localhost:8001` or the configured internal host
- request succeeds with valid internal token
- response is JSON and parseable

### 13.5 Inference works

- `POST /v1/brain/infer` with valid payload returns a generated answer
- answer is a string
- response includes `model`, `response`, `user_id`, and `request_id`
- result matches Server 1 contract

### 13.6 Invalid authentication is rejected

- missing token returns `401`
- malformed token returns `401`
- wrong token returns `401`

### 13.7 Server 2 cannot access the vault directly

- confirm there are no code paths for direct DB or vault access
- confirm Server 2 receives no raw vault data
- confirm Server 1 is the sole authorized boundary for data selection

### 13.8 Only Qwen3.5-4B is loaded

- model registry lists only `Qwen3.5-4B`
- no additional model is loaded during startup
- Server 2 is not running a general-purpose secondary model

### 13.9 Response format matches Server 1 contract

- response JSON matches the schema in this document
- no extra data is required from applications
- all fields are consistent and serializable

---

## Final required configuration summary

### Server 2 API URL/port expected by Server 1

- Default development URL: `http://localhost:8001`
- Docker network alternative: `http://aura-server2:8001`
- production internal URL: `http://<server2-host>:8001`

### Model path expected

```text
/home/pranav_gorde/aura/server2/models/Qwen3.5-4B
```

Container mount target:

```text
/models/Qwen3.5-4B
```

### Docker networking method

- Development on same laptop: localhost + Docker port mapping
- Same Compose project: internal Docker network
- Private LAN: trusted internal network only

### Authentication method

- `Authorization: Bearer <SERVER2_INTERNAL_TOKEN>`

### Exact environment variables Server 1 needs

```bash
AI_SERVER_URL=http://localhost:8001
AI_SERVER_INTERNAL_TOKEN=replace-with-shared-secret
AI_BRAIN_MODEL=Qwen3.5-4B
AI_BRAIN_TIMEOUT_MS=30000
```

### Exact environment variables Server 2 needs

```bash
HOST=0.0.0.0
PORT=8001
MODEL_NAME=Qwen3.5-4B
MODEL_PATH=/models/Qwen3.5-4B
INTERNAL_API_TOKEN=replace-with-shared-secret
```

### Any changes Server 1 will eventually require

The current Server 1 implementation already has a default `AI_SERVER_URL` value and a provider abstraction pattern. The eventual changes are:

- add a real remote provider client to replace the current mock provider
- wire the final `PersonalBrainService` flow to the `POST /v1/brain/infer` call
- add request timeout handling and retry behavior
- add token validation against the Server 2 shared secret
- ensure the minimal-context contract is enforced on every call

### Information not determined from the existing code

The following cannot be confirmed from the current Server 1 implementation alone:

- whether this laptop has GPU acceleration enabled
- exact Docker runtime to use for the model (CPU-only vs CUDA)
- whether `Qwen3.5-4B` is already in the exact format expected by a chosen runtime without additional conversion
- whether the final production host will be localhost, a Docker service name, or a LAN host
- the exact auth secret value for the internal model service
- the final Server 2 app package structure because no Server 2 files exist yet

These are design decisions that must be set explicitly when the Server 2 container is built, but they do not change the architecture requirement: Server 1 remains the ecosystem boundary; the Personal Brain is Qwen3.5-4B on Server 2; Server 2 does not access the Personal Vault or become the user database.
