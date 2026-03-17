# Suggested approach:
# Add tools one at a time: review_card, create_card, list_cards, list_tags
# See CLAUDE.md for the full API reference and tool specifications.
import os
from enum import Enum

import httpx
from dotenv import load_dotenv
from mcp.server import fastmcp

load_dotenv()


class ReviewRating(int, Enum):
    """
    Rating scale for card reviews (inspired by SM-2):
    - AGAIN (0): Complete failure, reset progress
    - HARD (1): Significant difficulty, shorter interval
    - GOOD (2): Correct with some effort, normal interval
    - EASY (3): Effortless recall, longer interval
    """

    AGAIN = 0
    HARD = 1
    GOOD = 2
    EASY = 3


BASE_API_URL = os.getenv("NOTE_TAKER_API_URL")
API_KEY = os.getenv("NOTE_TAKER_API_KEY")
HEADERS = {"X-API-KEY": API_KEY}

mcp = fastmcp.FastMCP("note-taker-plus")


@mcp.tool()
async def get_due_cards(tag: str | None = None, limit: int = 20):
    params: dict[str, int | str] = {"limit": limit}
    if tag is not None:
        params["tag"] = tag

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_API_URL}/cards/due", params=params, headers=HEADERS
        )
    return r.json()["cards"]


@mcp.tool()
async def review_card(card_id: int, rating: ReviewRating):
    url = f"{BASE_API_URL}/cards/{card_id}/review"
    data = {"rating": rating.value}

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=data, headers=HEADERS)

    return r.json()


if __name__ == "__main__":
    mcp.run()
