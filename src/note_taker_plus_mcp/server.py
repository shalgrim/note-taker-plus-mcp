import os
import sys
from enum import Enum, StrEnum, auto

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


class RequestType(StrEnum):
    GET = auto()
    POST = auto()


BASE_API_URL = os.getenv("NOTE_TAKER_API_URL")
API_KEY = os.getenv("NOTE_TAKER_API_KEY")
HEADERS = {"X-API-KEY": API_KEY}

mcp = fastmcp.FastMCP("note-taker-plus")


async def request(
    request_type: RequestType,
    url: str,
    params: dict | None = None,
    data: dict | None = None,
) -> dict:
    async with httpx.AsyncClient() as client:
        params = params or {}
        data = data or {}
        request_params = {"params": params, "headers": HEADERS}
        if request_type == RequestType.POST:
            request_params["json"] = data

        try:
            r = await getattr(client, request_type.value)(url, **request_params)
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(
                f"Error: Status code {e.response.status_code} received.",
                file=sys.stderr,
            )
            print(f"Response text: {e.response.text}", file=sys.stderr)
            return {
                "error": f"API returned {e.response.status_code}",
                "detail": e.response.text,
            }
        except httpx.RequestError as e:
            print("Could not reach API", file=sys.stderr)
            print(f"Detail: {str(e)}", file=sys.stderr)
            return {"error": "Could not reach API", "detail": str(e)}

        return r.json()


@mcp.tool()
async def get_card(card_id: int) -> dict:
    r = await request(RequestType.GET, f"{BASE_API_URL}/cards/{card_id}")
    return r


@mcp.tool()
async def get_due_cards(
    tag: str | None = None, limit: int = 20
) -> list[dict] | dict[str, str]:
    params: dict[str, int | str] = {"limit": limit}
    if tag is not None:
        params["tag"] = tag
    r = await request(RequestType.GET, f"{BASE_API_URL}/cards/due", params)
    return r["cards"]


@mcp.tool()
async def review_card(card_id: int, rating: ReviewRating):
    data = {"rating": rating.value}
    r = await request(
        RequestType.POST, f"{BASE_API_URL}/cards/{card_id}/review", data=data
    )

    return r


if __name__ == "__main__":
    mcp.run()
