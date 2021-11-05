"""
Метод для авторизации через госуслуги.
Если работает обычная авторизация, то импортировать этот модуль не нужно,
чтобы не устанавливать дополнительно тяжеловесный playwright
"""
from dnevnik import Dnevnik
from asyncio import sleep
from aiohttp import ClientConnectionError
try:
    from playwright.async_api import async_playwright
except ImportError:
    raise ImportError("Need install playwright lib.\nUsage:\n\tpip install playwright\n\tinstall playwright.")


class GosDiary:
    """Класс создания Dnevnik после успешной авторизации.

    Для его работы требуется передать login, password, region url

    :example:
    >>> import asyncio
    >>> from session_gos import GosDiary
    >>> from gos_regions import KIROV_REGION  # импортируйте свой регион, этот для примера
    >>> async def main():
    ...     login, password = "71234567890", "qwerty123"
    ...     gos_d = GosDiary(login, password, region_url=KIROV_REGION)
    ...     diary = await gos_d.auth()
    ...     async with diary as d:
    ...         await d.get_class_users()
    ...         # ... далее работа аналогична с классом Dnevnik
    ...asyncio.get_event_loop().run_until_complete(main())
    """
    def __init__(self, login, password, region_url):
        self.__login: str = login
        self.__password: str = password
        self.region_url: str = region_url

    async def auth(self) -> Dnevnik:
        """Авторизация через госуслуги с помощью эмуляции браузера.

        Сначала переходит на страницу региона, затем на госуслуги, там происходит авторизация с получением
        необходимых cookies для дальнейшей работы.


        TODO добавить 2FA подтверждение
        """
        async with async_playwright() as p:
            browser = await p.firefox.launch()
            page = await browser.new_page()
            await page.goto(self.region_url)
            # переход на госуслуги
            await sleep(0.3)
            await page.click("a.login__pubservices-link:nth-child(1)")
            await page.fill("#login", self.__login)
            await page.fill("#password", self.__password)
            await sleep(0.3)
            await page.click("#loginByPwdButton")
            # здесь должна быть дополнительная проверка на 2FA ответ, нужна помощь в получении нужных полей,
            # так как нет аккаунта!
            cookies = await page.context.cookies()
            if "DnevnikAuth_a" in [c["name"] for c in cookies]:
                dn_a = [c["value"] for c in cookies if c["name"] == "DnevnikAuth_a"][0]
                t0 = [c["value"] for c in cookies if c["name"] == "t0"][0]
                await browser.close()
                d = Dnevnik(self.__login, self.__password, cookies={"DnevnikAuth_a": dn_a, "t0": t0})
                d.diary_api.parse_ids()
                return d
            await browser.close()
            raise ClientConnectionError("Auth error")
