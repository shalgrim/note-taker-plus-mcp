# CLAUDE.md

## What We're Building

An MCP (Model Context Protocol) server that exposes a spaced repetition API ([note-taker-plus](https://github.com/scotthalgrim/note-taker-plus)) as tools for any MCP client (Claude Desktop, Cursor, etc.). This lets you quiz yourself, create flashcards, and review cards from any AI assistant that supports MCP.

This is a learning project — building it by hand to understand MCP server development from the ground up.

## note-taker-plus API Reference

**Base URL:** `https://note-taker-plus-production.up.railway.app`
**Auth:** `X-API-Key` header on every request

### Key Endpoints

#### GET /cards/due
Get cards due for review (spaced repetition).

Query params:
- `tag` (str, optional) — filter by tag name
- `limit` (int, default 20, max 100) — max cards to return

Response:
```json
{
  "cards": [
    {
      "id": 1,
      "front": "What is PKCE?",
      "back": "Proof Key for Code Exchange...",
      "hint": null,
      "source_id": null,
      "status": "active",
      "ease_factor": 2.5,
      "interval_days": 6,
      "repetitions": 3,
      "next_review": "2026-03-16T00:00:00",
      "last_reviewed": "2026-03-10T00:00:00",
      "created_at": "2026-03-01T00:00:00",
      "updated_at": "2026-03-10T00:00:00",
      "tags": [{"id": 1, "name": "oauth", "color": null, "created_at": "..."}]
    }
  ],
  "total_due": 5
}
```

#### POST /cards/{card_id}/review
Submit a review for a card.

Request body:
```json
{
  "rating": 2,
  "response_time_ms": 5000
}
```

Rating values (SM-2):
- `0` = AGAIN (complete failure, reset to 1 day)
- `1` = HARD (shorter interval, ease_factor -= 0.15)
- `2` = GOOD (normal interval, interval *= ease_factor)
- `3` = EASY (longer interval, ease_factor += 0.15)

`response_time_ms` is optional.

#### POST /cards
Create a new card.

Request body:
```json
{
  "front": "Question text",
  "back": "Answer text",
  "hint": "Optional hint",
  "source_id": null,
  "tags": ["oauth", "security"]
}
```

Tags are passed as string names (created automatically if they don't exist).

#### GET /cards
List cards with filtering.

Query params:
- `page` (int, default 1)
- `per_page` (int, default 20, max 100)
- `status` (str, optional) — "draft", "active", "suspended", "mastered"
- `tag` (str, optional) — filter by tag name
- `source_id` (int, optional)

Response:
```json
{
  "cards": [...],
  "total": 68,
  "page": 1,
  "per_page": 20
}
```

#### GET /tags
List all tags.

Response: array of `{"id": 1, "name": "oauth", "color": null, "created_at": "..."}`

#### GET /health
Health check (no auth required).

### Enums

**CardStatus:** "draft", "active", "suspended", "mastered"

**ReviewRating:** 0 (AGAIN), 1 (HARD), 2 (GOOD), 3 (EASY)

**SourceType:** "raindrop", "readwise", "chrome_extension", "manual", "alfred", "ios_shortcut"

## MCP Tools to Expose

Build in this order:

1. **`get_due_cards`** — wraps GET /cards/due. Accepts optional `tag` and `limit` params. Returns due cards.
2. **`review_card`** — wraps POST /cards/{id}/review. Accepts `card_id` and `rating` (0-3). Returns updated card.
3. **`create_card`** — wraps POST /cards. Accepts `front`, `back`, optional `hint` and `tags`. Returns created card.
4. **`list_cards`** — wraps GET /cards. Accepts optional filters (`status`, `tag`, `page`, `per_page`). Returns paginated list.
5. **`list_tags`** — wraps GET /tags. Returns all tags.

## Learning Goals

Concepts to understand deeply while building this:

### MCP Protocol
- **Protocol lifecycle:** initialize -> tools/list -> tools/call -> response
- **Transport mechanisms:** stdio (for local tools) vs HTTP+SSE (Streamable HTTP, for remote servers)
- **Tool registration:** How servers declare tools with names, descriptions, and input schemas
- **JSON-RPC:** MCP uses JSON-RPC 2.0 as its message format

### OAuth & Auth Patterns
- **OAuth 2.0 authorization code flow** — the standard grant type for web apps
- **PKCE (Proof Key for Code Exchange)** — extension for public clients (mobile, SPA) that can't store a client_secret. Uses code_verifier/code_challenge pair.
- **Token refresh** — using refresh_token to get new access_token without user interaction
- **Dynamic Client Registration (RFC 7591)** — allows clients to register programmatically instead of manual UI registration. MCP spec recommends this so non-human agents can self-register.
- **Opaque tokens** — tokens that are references/pointers rather than self-contained JWTs. The issuer maintains a lookup table. Useful for proxying/brokering scenarios where you don't want downstream clients to see the real provider token.
- **Token brokering** — acting as an intermediary between a client and an OAuth provider, translating between different auth capabilities (e.g., bridging static client registration to dynamic client registration)

### MCP Security
- **Tool poisoning** — malicious tool descriptions that contain hidden instructions to manipulate how the AI uses *other* tools. The attack vector is the description text, not the tool name.
- **Cross-server tool shadowing** — a malicious server registers a tool with the same name as a trusted server's tool, intercepting calls meant for the legitimate tool.
- **Key distinction:** Poisoning corrupts the AI's *reasoning*. Shadowing *intercepts calls*. Both exploit the lack of tool context isolation across servers.
- **Rug pulls** — tool behavior changes after initial approval/review
- **Credential exfiltration** — tools designed to capture and leak auth tokens
- **Fine-grained runtime policies** — permission checks that go beyond OAuth scopes by inspecting tool call payloads at runtime (e.g., allow read_repository only for a specific org)

## Conventions

- Python virtual environments in `.venv`
- Dependencies managed with `requirements.in` + `uv pip compile` -> `requirements.txt`
- Dev dependencies in `requirements-dev.in` -> `requirements-dev.txt`
- Tests use pytest
- Use the official `mcp` Python SDK (FastMCP) — `pip install mcp[cli]`
- Use `httpx` for async HTTP calls to the note-taker-plus API
- Configuration via `.env` file (see `.env.example`)
