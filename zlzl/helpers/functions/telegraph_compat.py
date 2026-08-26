"""Small compatibility layer for the legacy TelegraphPoster API."""

from __future__ import annotations

from telegraph import Telegraph


class TelegraphPoster:
    """Expose the methods ZTele uses without the legacy lxml-bound package."""

    def __init__(self, use_api: bool = True) -> None:
        del use_api
        self._client = Telegraph()
        self._ready = False

    def create_api_token(self, short_name: str) -> None:
        if not self._ready:
            self._client.create_account(short_name=short_name[:32] or "ZTele")
            self._ready = True

    def post(
        self,
        *,
        title: str,
        author: str,
        author_url: str,
        text: str,
    ) -> dict[str, str]:
        if not self._ready:
            self.create_api_token(author)
        return self._client.create_page(
            title=title,
            html_content=text,
            author_name=author,
            author_url=author_url,
        )
