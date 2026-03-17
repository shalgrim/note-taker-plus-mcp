# Suggested approach:
# Add tools one at a time: review_card, create_card, list_cards, list_tags
# See CLAUDE.md for the full API reference and tool specifications.
import os
import sys
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
async def get_card(card_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_API_URL}/cards/{card_id}", headers=HEADERS)
    try:
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"Error: Status code {e.response.status_code} received.", file=sys.stderr)
        print(f"Response text: {e.response.text}", file=sys.stderr)
        return {
            "error": f"API returned {e.response.status_code}",
            "detail": e.response.text,
        }
    return r.json()


@mcp.tool()
async def get_due_cards(
    tag: str | None = None, limit: int = 20
) -> list[dict] | dict[str, str]:
    params: dict[str, int | str] = {"limit": limit}
    if tag is not None:
        params["tag"] = tag

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{BASE_API_URL}/cards/due", params=params, headers=HEADERS
            )
    except httpx.RequestError as e:
        print("Could not reach API", file=sys.stderr)
        print(f"Detail: {str(e)}", file=sys.stderr)
        return {"error": "Could not reach API", "detail": str(e)}

    try:
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"Error: Status code {e.response.status_code} received.", file=sys.stderr)
        print(f"Response text: {e.response.text}", file=sys.stderr)
        return {
            "error": f"API returned {e.response.status_code}",
            "detail": e.response.text,
        }
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
