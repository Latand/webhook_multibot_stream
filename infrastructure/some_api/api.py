from infrastructure.some_api.base import BaseClient


class HearthstoneApi(BaseClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://omgvamp-hearthstone-v1.p.rapidapi.com"
        super().__init__(base_url=self.base_url)

    @property
    def headers(self):
        return {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "omgvamp-hearthstone-v1.p.rapidapi.com",
        }

    async def get_info(self):
        status, info = await self._make_request(
            "GET",
            url="/info",
            headers=self.headers,
        )
        if status == 200:
            return info
        else:
            raise ValueError(f"Got status {status} for /info: {info}")
