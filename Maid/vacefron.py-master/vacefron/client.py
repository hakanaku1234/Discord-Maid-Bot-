from asyncio import get_event_loop
from re import search
from typing import Any, Tuple

from aiohttp import ClientSession

from .errors import BadRequest, HTTPException, InternalServerError, NotFound
from .image import Image


def _parse_text(text: str) -> str:
    replacements = {
        " ": "%20",
        "!": "%21",
        '"': "%22",
        "#": "%23",
        "$": "%24",
        "%": "%25",
        "&": "%26",
        "'": "%27",
        "(": "%28",
        ")": "%29",
        "*": "%2A",
        "+": "%2B",
        ",": "%2C",
        "-": "%2D",
        ".": "%2E",
        "/": "%2F",
        "=": "%3D",
        "@": "%40",
        ":": "%3A",
        ";": "%3B",
        "^": "%CB%86",
        "_": "%5F",
        "©": "%C2%A9"
        }
    return text.translate(str.maketrans(replacements))


class Client:

    def __init__(self, session: ClientSession = None) -> None:
        self.session = ClientSession(loop = get_event_loop()) or session
        self._api_url = "https://vacefron.nl/api"

    async def _check_url(self, url: str):  # return_response=False):
        response = await self.session.get(url)
        if response.status == 200:
            return url
        elif response.status == 400:
            raise BadRequest((await response.json()).get("message"))
        elif response.status == 404:
            raise NotFound((await response.json()).get("message"))
        elif response.status == 500:
            raise InternalServerError((await response.json()).get("message"))
        else:
            raise HTTPException(response, (await response.json()).get("message"))

    # can anyone improve this? PRs are more than welcome.

    # Json/URL

    async def discord_server(self, creator: bool = False) -> Tuple[Any, str]:
        api = await self.session.get(self._api_url)
        support_server = (await api.json()).get("discord_server")
        if creator:
            return support_server, "https://discord.gg/yCzcfju"

        return support_server

    # Image

    async def car_reverse(self, text: str) -> Image:
        text = _parse_text(str(text))
        url = await self._check_url(f"{self._api_url}/carreverse?text={text}")
        return Image(url, self.session)

    async def change_my_mind(self, text: str) -> Image:
        text = _parse_text(str(text))
        url = await self._check_url(f"{self._api_url}/changemymind?text={text}")
        return Image(url, self.session)

    async def first_time(self, user: str) -> Image:
        url = await self._check_url(f"{self._api_url}/firsttime?user={user}")
        return Image(url, self.session)

    async def grave(self, user: str) -> Image:
        url = await self._check_url(f"{self._api_url}/grave?user={user}")
        return Image(url, self.session)

    async def iam_speed(self, user: str) -> Image:
        url = await self._check_url(f"{self._api_url}/iamspeed?user={user}")
        return Image(url, self.session)

    async def i_can_milk_you(self, user: str, user2: str = None) -> Image:
        url = f"{self._api_url}/icanmilkyou?user1={user}"
        url = await self._check_url(url)
        if user2 is not None:
            url += f"&user2={user2}"
        return Image(url, self.session)

    async def heaven(self, user: str) -> Image:
        url = await self._check_url(f"{self._api_url}/heaven?user={user}")
        return Image(url, self.session)

    async def npc(self, text: str, text2: str) -> Image:
        url = await self._check_url(f"{self._api_url}/npc?text1={text}&text2={text2}")
        return Image(url, self.session)

    async def stonks(self, user: str) -> Image:
        url = await self._check_url(f"{self._api_url}/stonks?user={user}")
        return Image(url, self.session)

    async def table_flip(self, user: str) -> Image:
        url = await self._check_url(f"{self._api_url}/tableflip?user={user}")
        return Image(url, self.session)

    async def water(self, text: str) -> Image:
        text = _parse_text(str(text))
        url = await self._check_url(f"{self._api_url}/water?text={text}")
        return Image(url, self.session)

    async def wide(self, image: str) -> Image:
        url = await self._check_url(f"{self._api_url}/wide?image={image}")
        return Image(url, self.session)

    async def rank_card(self, username: str, avatar: str, level: int, rank: int, current_xp: int,
                        next_level_xp: int, previous_level_xp: int, custom_background: str = None,
                        xp_color: str = None, is_boosting: bool = False) -> Image:
        username = _parse_text(str(username))
        url = f"?username={username}&avatar={avatar}&level={level}&rank={rank}&currentxp={current_xp}" \
              f"&nextlevelxp={next_level_xp}&previouslevelxp={previous_level_xp}"

        if custom_background is not None:
            url += f"&custombg={custom_background}"
        if xp_color is not None:
            if not search(r'^(?:[0-9a-fA-F]{3}){1,2}$', str(xp_color)):
                raise BadRequest("Invalid HEX value. You're only allowed to enter HEX (0-9 & A-F)")
            else:
                url += f"&xpcolor={xp_color}"
        if is_boosting:
            url += f"&isboosting=true"

        actual_url = await self._check_url(f"{self._api_url}/rankcard{url}")
        return Image(actual_url, self.session)

    async def close(self) -> None:
        if not self.session.closed:
            await self.session.close()
