# AURA Server 2 — Personal Brain Implementation

**Implementation Phase**: Build Server 2, don't just specify it.

---

## 1. DEFINITIVE AURA ARCHITECTURE

AURA consists of three major server roles:

### SERVER 1 — AURA CORE
- Authentication
- Aura ID
- User identity
- Application/API gateway
- Ecosystem coordination
- Sends application requests to the Personal Brain
- Does NOT directly access the user's personal vault for application reasoning

### SERVER 2 — PERSONAL BRAIN
- Contains the user's Personal Brain LLM
- This is the intelligence layer
- For the current prototype, the Personal Brain LLM is: **Qwen3.5-4B**
- This exact model is already downloaded locally
- Do NOT replace it
- Do NOT download another model
- Do NOT create a fake/custom LLM to replace it

### SERVER 3 — PERSONAL VAULT
- Future personal storage/data server
- Contains the user's long-term personal data
- NOT being implemented now

**Fundamental Architecture:**
```
APPLICATION
    ↓
SERVER 1 (AURA CORE)
    ↓
SERVER 2 (PERSONAL BRAIN)
    ↓
PERSONAL VAULT (SERVER 3 - FUTURE)
```

**Key Principle: APPLICATIONS ARE DOORS. THE PERSONAL BRAIN IS THE DESTINATION.**

---

## 2. WHAT "PERSONAL BRAIN" MEANS

The Personal Brain is NOT:
- A database table
- CRUD code
- A Python rules engine
- A keyword router
- A static context builder
- A mock response generator

**The Personal Brain IS the actual Qwen3.5-4B LLM running as a service.**

Python/server infrastructure exists to:
- Load the model
- Expose the model through an API
- Manage requests
- Identify the user/brain
- Construct controlled context
- Communicate with Server 1
- Communicate with the future Server 3
- Communicate with future generalized LLMs
- Handle logging, health checks and errors

**The actual understanding/reasoning/personalization must be performed by Qwen3.5-4B.**

Do NOT implement a fake "brain" using hard-coded if/else logic.

---

## 3. MODEL LOCATION

The Qwen3.5-4B model has ALREADY been downloaded.

**Expected location:**
```
~/aura/server2/models/Qwen3.5-4B/
```

**Directory contains:**
- config.json
- model.safetensors.index.json
- model.safetensors-00001-of-00002
- model.safetensors-00002-of-00002
- tokenizer.json
- tokenizer_config.json
- merges.txt
- vocab.json
- chat_template.jinja
- preprocessing configuration files

**FIRST inspect the actual filesystem and verify the model path.**

Do NOT download the model again.

---

## 4. FIXED MODEL DECISION

For this project:
**Qwen3.5-4B = Personal Brain model**

This is a project-level architectural decision.

Do not propose replacing it with:
- Another Qwen model
- Llama
- Gemma
- Mistral
- Phi
- Any other model

Future model experimentation is outside this task.

---

## 5. SERVER 2 RESPONSIBILITY

Build Server 2 as an independent service.

It must:
1. Start the Qwen3.5-4B model
2. Keep the model loaded when possible
3. Expose a clean HTTP API
4. Accept Brain requests
5. Generate real responses using Qwen3.5-4B
6. Support user/brain identity
7. Support future personal-vault context
8. Support future generalized-LLM delegation
9. Return structured responses
10. Provide health/readiness endpoints
11. Provide useful logging
12. Be Docker-ready
13. Be easy to move to another laptop later

---

## 6. DO NOT BUILD SERVER 3

Absolutely DO NOT implement:
- Server 3
- Object storage
- Full personal vault
- S3
- MinIO
- Qdrant as the personal vault
- Production storage infrastructure
- User's complete personal-data database

You may define an interface/contract for future vault access, but it must remain an interface/stub only.

Server 2 must be able to say conceptually:
> "I will receive personal context from the vault in the future."

But Server 2 must NOT create Server 3.

---

## 7. DO NOT BUILD THE GENERAL LLM SERVER

Future Server 2 functionality may eventually include access to larger/general models, but NOT now.

For this implementation:
**ONLY Qwen3.5-4B**

Do not download or configure:
- Large LLMs
- Multiple models
- Model routing between several models
- External model providers

Create clean abstractions where useful so future models can be added without rewriting the Brain.

---

## 8. PERSONAL BRAIN REQUEST FLOW

Implement this conceptual flow:

```
Application
    ↓ user query
Server 1
    ↓ authenticated Brain request
Server 2
    ↓ identify user's Brain
    ↓ retrieve/receive available personal context
    ↓ construct Brain prompt/context
Qwen3.5-4B
    ↓ reasoning + personalization
Personal Brain response
    ↓
Server 1
    ↓
Application
```

The application should never need to understand how the Brain reasons.

---

## 9. EXAMPLE OF INTENDED BEHAVIOR

**Example user query:**
> "Should I go to the gym tonight?"

**In the future, the Brain could receive personal context such as:**
- Meeting at 6 PM
- Exam tomorrow
- Poor sleep last night
- Planned workout today
- Current study priority

**The Brain LLM should reason over this context and produce a personalized response.**

**Architectural point:**
THE PYTHON SERVICE SHOULD NOT DECIDE THE ANSWER.

Qwen3.5-4B should reason over the supplied context.

---

## 10. OUT-OF-CONTEXT QUERY / FUTURE GENERAL LLM

Eventually:

**User:** "Teach me DBMS."

**Personal Brain:**
1. Understands the request
2. Examines available personal context
3. Determines what the user already knows
4. Constructs a generalized-learning request
5. Future generalized LLM receives only the necessary information
6. Generalized LLM returns the broad explanation
7. Personal Brain receives it
8. Qwen3.5-4B personalizes it using the user's context
9. Brain returns the final response

Example: User knows SQL.
The future Brain could construct: "Teach this user DBMS, but avoid basic SQL concepts because the user already understands SQL."

**That generalized LLM functionality is FUTURE.**

Do NOT implement the large model now.

However, create a clean provider interface if appropriate so this future architecture does not require redesigning Server 2.

---

## 11. PERSONAL VAULT CONTEXT

**Future architecture:**
```
Server 3
    ↓ user's personal data
Personal Brain
```

Only the Personal Brain should have access to the user's personal vault.

Applications should NOT directly query the vault.

**For the current implementation, create a clean VaultProvider interface such as:**
```python
get_user_context(user_id)
search_user_memory(user_id, query)
store_brain_output(user_id, data)
```

**BUT:**
Use a development/mock implementation ONLY where necessary for testing.

Do not pretend the mock vault is the real production vault.

---

## 12. BRAIN IDENTITY

Every user has:
```
Aura ID
    ├── Personal Brain
    └── Personal Vault
```

Server 1 already manages user identity.

Server 2 must support brain identity in a way that can be mapped to the user's Aura ID.

Do not:
- Create a second unrelated user-registration system
- Require users to register again on Server 2

The Brain should be associated with the identity established by Server 1.

---

## 13. API DESIGN

Create a clean Server 2 API.

**At minimum implement:**

### GET /health
Health check endpoint

### GET /ready
Readiness check endpoint (model loaded, service ready)

### POST /v1/brain/query
Main query endpoint

**Request schema:**
```json
{
    "aura_id": "user-123",
    "brain_id": "brain-456",
    "query": "Should I go to the gym tonight?",
    "context": {
        "aura_id": "user-123",
        "brain_id": "brain-456",
        "meeting_at": "6 PM",
        "sleep_quality": "poor"
    }
}
```

**Response schema:**
```json
{
    "aura_id": "user-123",
    "brain_id": "brain-456",
    "response": "Based on your poor sleep and meeting at 6 PM, light exercise might be better...",
    "model": "Qwen3.5-4B"
}
```

Do not expose internal model implementation details unnecessarily.

---

## 14. MODEL RUNTIME

**FIRST inspect:**
- Available GPU
- Available VRAM
- Available system RAM
- Python version
- Docker availability
- Existing Server 2 files
- Qwen3.5-4B README/configuration
- Installed ML dependencies

**Then choose the most appropriate local inference runtime for THIS MACHINE.**

Possible technologies may include:
- Transformers
- vLLM
- Another appropriate local inference runtime

Do not blindly install everything.

Choose the simplest reliable runtime that can actually run Qwen3.5-4B on this laptop.

The model must be loaded from the EXISTING local model directory.

---

## 15. RESOURCE EFFICIENCY

This is a prototype.

Do not create unnecessary infrastructure.

Avoid:
- Downloading duplicate models
- Unnecessary databases
- Unnecessary containers
- Unnecessary vector databases
- Unnecessary services

Keep Server 2 focused:
- API
- Qwen3.5-4B
- Provider abstractions
- Health/readiness
- Docker

---

## 16. DOCKER

Create a Docker setup for Server 2.

The Docker architecture must allow:
- Model directory mounted into the container OR copied intentionally
- Persistent model availability
- Configurable host/port
- GPU support if available
- CPU fallback if practical
- Environment configuration
- Health checking

**IMPORTANT:**
The Docker image should NOT silently download another copy of Qwen3.5-4B during every build.

The already downloaded model should be reused.

We eventually want to be able to move Server 2 to another machine.

---

## 17. SERVER 1 INTEGRATION

Inspect the existing Server 1 implementation before creating the integration.

Find its existing:
- Brain provider abstraction
- Brain API
- Configuration
- Authentication
- Aura/user identity
- Request/response schemas

Then implement Server 2's interface so Server 1 can communicate with it cleanly.

**Do NOT unnecessarily rewrite Server 1.**

If Server 1 needs a small configuration change such as:
```
BRAIN_SERVER_URL
```

Make the minimal change required.

Do not break existing Server 1 authentication or APIs.

---

## 18. SECURITY

Server 2 must NOT expose unrestricted access.

At minimum:
- Validate requests
- Validate Aura/Brain identity
- Support service-to-service authentication
- Never accept arbitrary user identity without validation
- Do not expose model internals unnecessarily
- Do not log private user context in plaintext unnecessarily
- Do not leak one user's context into another user's request

Design for strict user/Brain isolation.

---

## 19. TESTING

Create tests for:
1. Health endpoint
2. Readiness endpoint
3. Request schema validation
4. Brain identity validation
5. Basic model inference
6. Response schema
7. User isolation
8. Server 1 → Server 2 communication
9. Model unavailable behavior
10. Malformed request behavior

**At least one test must perform REAL Qwen3.5-4B inference if the machine can support it.**

If full model inference cannot run inside the normal test suite because of hardware/time constraints:
- Create a separate integration test
- Clearly document it
- Do not replace the actual model with a fake response while claiming the real model works

---

## 20. OBSERVABILITY

Provide:
- Startup logging
- Model loading status
- Inference timing
- Request IDs
- Health status
- Clear errors

Never log:
- Passwords
- JWT secrets
- Private user vault contents
- Sensitive raw context unnecessarily

---

## 21. PROJECT STRUCTURE

Use a clean structure similar to:

```
server2/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── ...
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── ...
│   ├── brain/
│   │   ├── engine.py
│   │   ├── prompts.py
│   │   ├── context.py
│   │   └── ...
│   ├── providers/
│   │   ├── brain_llm.py
│   │   ├── vault.py
│   │   └── general_llm.py
│   └── schemas/
│       └── ...
├── models/
│   └── Qwen3.5-4B/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements/
├── .env.example
└── README.md
```

Adapt this structure to the existing repository if one already exists.

Do not duplicate existing infrastructure unnecessarily.

---

## 22. IMPORTANT ARCHITECTURAL RULE

DO NOT implement a second "brain" around Qwen.

There should be exactly one actual intelligence engine:

**Qwen3.5-4B**

The surrounding Python code is infrastructure.

**CORRECT:**
```
Request
  ↓
Brain service
  ↓
Context construction
  ↓
Qwen3.5-4B
  ↓
Response
```

**WRONG:**
```
Request
  ↓
Python rule engine
  ↓
"Brain algorithm"
  ↓
fake/mock answer
```

**Qwen3.5-4B must be the actual reasoning engine.**

---

## 23. IMPLEMENTATION PROCESS

Follow this order:

### PHASE A — AUDIT
- Inspect Server 2 directory
- Inspect Server 1 contracts
- Inspect Qwen3.5-4B files
- Inspect machine hardware
- Inspect existing dependencies
- Report findings briefly

### PHASE B — FOUNDATION
- Create Server 2 application
- Configuration
- Logging
- API
- Schemas

### PHASE C — REAL QWEN RUNTIME
- Integrate the locally downloaded Qwen3.5-4B
- Load the actual model
- Implement inference
- Verify real generation

### PHASE D — PERSONAL BRAIN
- Brain request processing
- Context interface
- User/Brain identity
- Provider architecture
- Personalization prompt structure

### PHASE E — SERVER 1 CONNECTION
- Connect Server 1 to Server 2
- Service-to-service authentication
- Test end-to-end request

### PHASE F — DOCKER
- Dockerfile
- Compose configuration
- Model mounting
- GPU configuration where appropriate

### PHASE G — TESTING
- Unit tests
- Integration tests
- Real model inference test
- End-to-end test

### PHASE H — DOCUMENTATION
Create:
- SERVER_2_ARCHITECTURE.md
- SERVER_2_SETUP.md
- SERVER_2_STATUS.md

Document exactly what is implemented and what remains future work.

---

## 24. ABSOLUTE SCOPE RESTRICTIONS

DO NOT:
- Build Server 3
- Build the personal vault
- Download another LLM
- Replace Qwen3.5-4B
- Build a large/general LLM
- Build multiple model routing
- Create fake intelligence instead of using Qwen
- Create a second user registration system
- Bypass Server 1 identity
- Allow apps to directly access the vault
- Redesign Server 1 unnecessarily

---

## 25. FINAL ACCEPTANCE CRITERIA

Server 2 is complete for this phase only when:

- [ ] Server 2 starts successfully
- [ ] Qwen3.5-4B loads from the existing local model directory
- [ ] Real Qwen3.5-4B inference works
- [ ] /health works
- [ ] /ready works
- [ ] /v1/brain/query works
- [ ] Brain identity is represented
- [ ] User isolation exists
- [ ] Server 1 can communicate with Server 2
- [ ] Server-to-server authentication exists
- [ ] Docker setup exists
- [ ] Model is not downloaded again
- [ ] No Server 3 implementation exists
- [ ] No large/general LLM is installed
- [ ] Tests pass
- [ ] Documentation accurately describes the implementation

---

## 26. MOST IMPORTANT FINAL INSTRUCTION

**Do not stop after creating documentation.**

**Actually IMPLEMENT Server 2.**

Do not claim Qwen3.5-4B works unless you perform a real inference test.

Do not substitute a mock provider for the real Brain implementation.

**The prototype's actual Personal Brain is: Qwen3.5-4B**

Everything else exists to give that model the infrastructure required to function as the Personal Brain of the AURA ecosystem.

Begin by auditing the existing Server 2 directory and machine capabilities, then proceed through implementation.

---

## Addendum: Quick Reference

**Model Configuration:**
- Architecture: Qwen3.5-4B
- Type: Causal Language Model with Vision Encoder
- Parameters: 4B
- Hidden Dimension: 2560
- Context Length: 262,144 tokens (native), up to 1,010,000 tokens (extensible)
- Supported Languages: 201+ languages and dialects

**Expected Machine Specs (from audit):**
- OS: Linux x86_64
- CPU: 12-core Intel Core 5 120U
- RAM: 14 GB
- GPU: None (CPU-only fallback required)
- Python: 3.14.4
- Docker: Not installed (create Docker config anyway for future portability)

**Runtime Stack:**
- FastAPI for HTTP API
- Uvicorn as ASGI server
- Transformers for model loading and inference
- PyTorch 2.13.0 for computation
- Pydantic for schema validation

**Do not blindly follow generic ML deployment patterns. This is the AURA Personal Brain.**
