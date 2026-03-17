# note-taker-plus-mcp

An MCP server that exposes a spaced repetition API as tools for AI assistants. Built as a learning project to understand MCP server development from the ground up.

## What It Does

Wraps the [note-taker-plus](https://github.com/scotthalgrim/note-taker-plus) spaced repetition API so any MCP-compatible client (Claude Desktop, Cursor, etc.) can:

- Get flashcards due for review
- Submit reviews with SM-2 spaced repetition ratings
- Create new flashcards
- Browse and filter cards by tag or status

## Tools

| Tool | Description |
|------|-------------|
| `get_due_cards` | Get flashcards due for review |
| `review_card` | Submit a review rating (0-3) for a card |
| `create_card` | Create a new flashcard |
| `list_cards` | List/filter cards by status or tag |
| `list_tags` | List all available tags |

## Setup

```bash
# Clone and set up
git clone https://github.com/scotthalgrim/note-taker-plus-mcp.git
cd note-taker-plus-mcp
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API key
```

## Status

Work in progress.
