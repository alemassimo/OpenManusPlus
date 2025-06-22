from typing import List, Optional

from atproto import Client
from pydantic import BaseModel, Field, PrivateAttr

from app.tool.base import BaseTool, ToolResult

# inserisci username e password come costanti
USERNAME = "YOURUSERNAME.bsky.social"
PASSWORD = "YOUR_API_PASSWORD"


class BskyPost(BaseModel):
    handle: str = Field(description="BlueSky user handle")
    text: str = Field(description="Post content")


class BskySearchResponse(ToolResult):
    query: str = Field(description="The search query that was executed")
    results: List[BskyPost] = Field(
        default_factory=list, description="List of posts found"
    )
    total_results: int = Field(default=0, description="Total number of posts found")

    def __str__(self):
        if self.error:
            return f"Error: {self.error}"
        result_text = [f"BlueSky search results for '{self.query}':"]
        for i, post in enumerate(self.results, 1):
            result_text.append(f"\n{i}. @{post.handle}: {post.text}")
        result_text.append(f"\nTotal results: {self.total_results}")
        return "\n".join(result_text)


class BskySearch(BaseTool):
    """A tool for searching BlueSky posts by keyword."""

    _client: Client = PrivateAttr()
    name: str = "bsky_search"
    description: str = "Search BlueSky posts by keyword."
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query for BlueSky posts.",
            },
            "limit": {
                "type": "integer",
                "description": "Number of posts to return (default 10).",
                "default": 10,
            },
        },
        "required": ["query"],
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = Client()
        self._client.login(USERNAME, PASSWORD)

    async def execute(self, query: str, limit: int = 10) -> BskySearchResponse:
        try:

            results = self._client.app.bsky.feed.search_posts(
                {"q": query, "limit": limit}
            )
            posts = [
                BskyPost(handle=post["author"]["handle"], text=post["record"]["text"])
                for post in results.posts
            ]
            return BskySearchResponse(
                status="success", query=query, results=posts, total_results=len(posts)
            )
        except Exception as e:
            return BskySearchResponse(
                status="error", query=query, error=str(e), results=[], total_results=0
            )


print("BskySearch tool loaded successfully.")
