import asyncio
from datetime import date
from typing import AsyncIterable, Optional
import logging

from aiohttp import ClientSession, ClientResponse
from aiohttp.client_exceptions import ClientConnectionError

from parsers import Parser, ParserDiary, ParserBirthdayCalendar, ParserUsers
from models import Diary, YearBirthday, Users


# FORMAT = "%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
# logging.basicConfig(format=FORMAT, level=logging.DEBUG, filename="dnevnik.log")


class Dnevnik:
    BASE_URI = "https://schools.dnevnik.ru/"
    AUTH_URI = "https://login.dnevnik.ru/login"
    CLASS_URI = BASE_URI + "class.aspx"
    SCHEDULES_URI = BASE_URI + "schedules"
    BIRTHDAY_URI = BASE_URI + "birthdays.aspx"
    MARKS_URI = BASE_URI + "marks.aspx"
    SCHOOL_URI = BASE_URI + "school.aspx"
    EXCEL_SCHEDULES_URI = BASE_URI + "excel.ashx"
    WEEK_DIARY_URI = "https://dnevnik.ru/currentprogress/result/"
    # задержка перед каждым запросом
    PER_REQUEST_SLEEP = 0.5

    def __init__(self, login, password, **kwargs):
        self.__login = login
        self.__password = password
        self._school = ""
        self._profile_id = ""
        self._class_id = ""
        if kwargs.get("headers"):
            self._headers = kwargs.pop("headers")
        else:
            self._headers = {"User-Agent": "Mozilla/5.0 (Wayland; Linux x86_64) AppleWebKit/537.36 ("
                                           "KHTML, like Gecko) Chrome/94.0.4606.72 Safari/537.36"}
        self.session = ClientSession(headers=self._headers, **kwargs)

    async def __aenter__(self):
        """Открытие сессии через контекстный менеджер"""
        # await self.auth()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def _request(self, method, uri, **kwargs) -> ClientResponse:
        """Wrapper отправки запроса. Делает 3 попытки подключения каждые 500мс.
        Если вернёт статус код отличный от 200 или время подключения истечёт, то выбросит ошибку"""
        for _ in range(3):
            await asyncio.sleep(self.PER_REQUEST_SLEEP)
            logging.debug(f"[{_ + 1} ] Connect to {uri} {kwargs}")
            resp = await self.session.request(method, uri, **kwargs)
            logging.debug(f"[{_ + 1} ] {uri} return {resp.status}")
            if resp.status == 200:
                return resp
        logging.exception(f"Response return {resp.status} code")
        raise ClientConnectionError(f"Response return {resp.status} code")

    async def _request_get(self, uri, **kwargs) -> ClientResponse:
        """wrapper get запросов"""
        return await self._request("GET", uri, **kwargs)

    async def _request_post(self, uri, **kwargs) -> ClientResponse:
        """wrapper post запросов"""
        return await self._request("POST", uri, **kwargs)

    @staticmethod
    def __get_class_id(html: str) -> str:
        """получение id класса, в котором находится авторизованный пользователь"""
        return Parser.parse_group_id(html)

    @staticmethod
    def _get_profile_id(html: str) -> str:
        """Получение id профиля"""
        return Parser.parse_profile_id(html)

    async def auth(self) -> bool:
        """Авторизация пользователя"""
        logging.debug(f"Trying auth")
        resp = await self._request_post(self.AUTH_URI, data={"login": self.__login, "password": self.__password})
        if self.__get_school_id(resp):
            resp = await resp.text()
            # class_id
            self._class_id = self.__get_class_id(resp)
            logging.debug(f"Get class id {self._class_id}")
            # profile_id
            self._profile_id = self._get_profile_id(resp)
            logging.debug(f"Get profile id {self._profile_id}")
            return True

    def __get_school_id(self, resp: ClientResponse):
        if resp.cookies.get("t0"):
            self._school = resp.cookies.get("t0").value
            logging.debug(f"Get school id {self._school}")
            return True
        raise ClientConnectionError("Auth error")

    async def get_schedule_excel(self):
        """TODO получить файл расписания своей группы за весь семестр с помощью запроса на версию для печати
        в формате excel"""
        """endpoint:
        https://schools.dnevnik.ru/excel.ashx?&action=gs&school=000&group=456&period=000
        """
        pass
        # resp = await self._request_get(self.BASE_URI + "print.ashx", params={"action": "gs",
        #                                                                      "school": self._school,
        #                                                                      "group": self._class_id,
        #                                                                      "period": ""})
        # file = await resp.read()
        # return file

    async def get_class_users(self) -> Users:
        """возвращает список одноклассников с ФИО и ссылкой на профиль (если он зарегистрирован в дневник.ру)"""
        resp = await self._request("GET", self.CLASS_URI, params={"class": self._class_id, "view": "members"})
        resp = await resp.text()
        users = ParserUsers(resp).create_model()
        return users

    async def search_people(self, name: str = "", group: str = "all",
                            school_group="", max_page: Optional[int] = None) -> AsyncIterable[Users]:
        """
        Поиск по параметрам. Если ничего не передано, вернёт всех пользователей.
        Если ничего не найдёт, вернёт пустой итератор
        :param name: поиск по Имени/Фамилии/Отчеству по отдельности или всё вместе
        :param group: поиск по категории. По умолчанию или при некорректном вводе по всем ищет.
        доступные категории групп: "all", "students", "staff", "administrators", "teachers", "management", "director"
        :param school_group: поиск по номеру класса
        :param max_page: максимальное число итераций. По умолчанию по всем страницам
        :return user: - Возвращает итератор
        """
        available_groups = ["all", "students", "staff", "administrators", "teachers", "management", "director"]
        if group not in available_groups:
            group = "all"
        if not max_page:
            max_page = 100_000
        params = dict(school=self._school, view="members", group=group, school_group=group, search=name)
        params["class"] = school_group

        for i in range(1, max_page+1):
            params["page"] = str(i)
            resp = await self._request("GET", self.SCHOOL_URI, params=params)
            resp = await resp.text()
            users = ParserUsers(resp).create_model()
            if users.count == 0:
                break
            yield users

    async def get_all_peoples(self, max_pages: Optional[int] = None) -> AsyncIterable[Users]:
        """Получить всех школьников и сотрудников школы
        Возвращает итератор объектов словарей вида {"name": "Ivan", "uri": "url"}"""
        if not max_pages:
            max_pages = 100_000
        for i in range(1, max_pages+1):
            resp = await self._request_get(self.SCHOOL_URI, params={"school": self._school, "view": "members",
                                                                    "page": str(i)})
            resp = await resp.text()
            users = ParserUsers(resp).create_model()
            if users.count == 0:
                break
            yield users

    async def birthdays_near(self, group="all", max_pages: Optional[int] = None) -> AsyncIterable[Users]:
        """Возвращает итератор людей (без даты), у кого будет сегодня и в ближайшую неделю день рождения
        :param group: тип поиска подгруппы людей. По умолчанию "all" доступные группы:
        "all", "students", "staff", "class"
        """
        available_groups = ["all", "students", "staff", "class"]
        if group not in available_groups:
            group = "all"
        if not max_pages:
            max_pages = 100
        for i in range(1, max_pages+1):
            resp = await self._request_get(self.BIRTHDAY_URI, params={"school": self._school, "group": group,
                                                                      "page": str(i)})
            resp = await resp.text()
            users = ParserUsers(resp).create_model()
            if users.count == 0:
                break
            yield users

    async def calendar_birthdays(self) -> YearBirthday:
        """Возвращает объект YearBirthday вида:


        YearBirthday:
            days: List[Day]
        Day:
            count: int
            day: int
            month: str
            url: str
        """
        resp = await self._request_get(self.BIRTHDAY_URI, params={"school": self._school, "view": "calendar"})
        resp = await resp.text()
        p = ParserBirthdayCalendar(resp).create_model()
        return p

    async def get_diary(self, period: str = date.today().strftime("%d.%m.%Y")) -> Diary:
        """Возвращает объект Дневника Diary с атрибутами:
        Diary:
            info: Info
            themes: List[Theme]
            attendances: List[Attendance]
            progress: List[Progress]
            schedules: List[Schedule]
            homeworks: List[Homework]


        Дату указывать в формате %d.%m.%Y. По умолчанию устанавливается сегодняшняя дата
        """
        year = period.split(".")[-1]
        url = f"{self.WEEK_DIARY_URI}{self._profile_id}/{self._school}/{year}/{period}"
        resp = await self._request_get(url)
        resp = await resp.text()
        model = ParserDiary(resp).gen_model
        return model

    async def close(self):
        await self.session.close()
