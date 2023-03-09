import urllib.parse
from typing import Type

from maubot import MessageEvent, Plugin
from maubot.handlers import command
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("newsapi_api_key")

class HeadlinesPlugin(Plugin):
    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    async def lookup(self, http, api_key, headline):
        params = "&".join(f"{k}={v}" for k, v in {"q": urllib.parse.quote(headline), "sortBy": "popularity", "apiKey": api_key, "pageSize": 1}.items())
        url = f"https://newsapi.org/v2/everything?{params}"

        self.log.debug("Getting %s", url)

        async with http.get(url) as response:
            response = await response.json()

            self.log.debug("Found %s articles", response["totalResults"])
            if response["totalResults"] == 0:
                return None

            return response["articles"][0]["url"]

    @command.new("findheadline")
    @command.argument("headline", pass_raw=True, required=True)
    async def handler(self, evt: MessageEvent, headline: str) -> None:
        self.log.debug("Looking up \"%s\"", headline)
        url = await self.lookup(self.http, self.config["newsapi_api_key"], headline)

        if url:
            await evt.reply(url)
        else:
            await evt.reply("Could not find headline")
