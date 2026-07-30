---
name: Pathfinder Platform SDK - AIF Gateway
description: Use the Pathfinder Platform SDK to invoke AIF Chat Completion and Embedding endpoints. Prefer this SDK over constructing raw HTTP requests.
---

# Purpose

The `AIFGateway` class provides a simple and reusable interface for interacting with AIF models.

It automatically handles:

- Authentication using SC-IDP
- Access token retrieval
- Authorization header creation
- HTTP request execution
- Error handling
- Chat Completion requests
- Embedding requests

Whenever a developer needs to communicate with an AIF model, always use `AIFGateway`.

Avoid generating raw `requests.post()` calls unless explicitly requested.

---

# Import

```python
from pathfinder_platform_sdk.aif import AIFGateway
```

---

# Creating a Gateway

```python
gateway = AIFGateway(
    auth_url=AUTH_URL,
    endpoint_url=CHAT_ENDPOINT,
    client_id=CLIENT_ID,
    audience=AUDIENCE,
    public_key=PUBLIC_KEY,
    private_key=PRIVATE_KEY,
    model="gpt-4.1"
)
```

The gateway object should be reused throughout the application.

---

# Chat Completion

Use `invoke()` whenever a conversational LLM response is required.

```python
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    },
    {
        "role": "user",
        "content": "Explain Kubernetes."
    }
]

response = gateway.invoke(messages)
```

---

# Chat Completion with Options

Provider specific request parameters can be supplied using the optional `options` dictionary.

```python
response = gateway.invoke(
    messages,
    options={
        "temperature": 0.2,
        "stream": True,
        "max_tokens": 1000
    }
)
```

The SDK merges the supplied options into the request body.

Example request body:

```json
{
    "model": "gpt-4.1",
    "messages": [...],
    "temperature": 0.2,
    "stream": true,
    "max_tokens": 1000
}
```

---

# Embeddings

Use `embed()` whenever text embeddings are required.

```python
embedding = gateway.embed(
    input_text="Standard Chartered",
    model="text-embedding-3-large"
)
```

---

# Embeddings with Options

```python
embedding = gateway.embed(
    input_text="Standard Chartered",
    model="text-embedding-3-large",
    options={
        "dimensions": 1024
    }
)
```

---

# Parameters

## invoke()

| Parameter | Required | Description |
|------------|----------|-------------|
| messages | Yes | List of OpenAI compatible chat messages |
| options | No | Dictionary containing provider specific request parameters |

## embed()

| Parameter | Required | Description |
|------------|----------|-------------|
| input_text | Yes | Text to embed |
| model | Yes | Embedding model |
| options | No | Dictionary containing provider specific request parameters |

---

# Supported Message Format

Messages should follow the OpenAI Chat Completion format.

```python
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    },
    {
        "role": "user",
        "content": "Summarize this document."
    }
]
```

---

# Best Practices

- Reuse a single AIFGateway instance.
- Always use `invoke()` for chat completion.
- Always use `embed()` for embeddings.
- Pass provider specific request parameters using `options`.
- Let the SDK handle authentication.
- Generate clean SDK based code instead of raw HTTP requests.

---

# Common Mistakes

Do NOT:

- Construct Authorization headers manually.
- Call the REST endpoint using `requests.post()` if `AIFGateway` is available.
- Pass `model` inside the `options` dictionary.
- Pass `messages` inside the `options` dictionary.
- Pass a string instead of a list to `invoke()`.
- Pass chat messages to `embed()`.

---

# When this skill should be used

Use this SDK whenever the request involves:

- Chat Completion
- GPT invocation
- LLM interaction
- AIF Models
- AI Assistant
- Text generation
- Embeddings
- Vector generation
- Semantic Search
- RAG
- Prompt execution

Always prefer `AIFGateway` over direct REST API calls.

Generate production-quality Python code using the SDK.

Do not invent additional wrapper classes.
