from datetime import date
from typing import AsyncIterable, Optional

from models import Diary, YearBirthday, Users
from session import DiaryAPI


class Dnevnik:
    """Высокоуровневый API для работы с dnevnik.ru"""

    def __init__(self, login, password, **kwargs):
        self.__login = login
        self.__password = password
        self.diary_api = DiaryAPI(login, password, **kwargs)

    async def __aenter__(self):
        """Открытие сессии через контекстный менеджер"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.diary_api.session.close()

    async def auth(self) -> bool:
        """Авторизация пользователя"""
        return await self.diary_api.auth()

    async def get_class_users(self) -> Users:
        """возвращает список одноклассников с ФИО и ссылкой на профиль (если он зарегистрирован в дневник.ру)"""
        return await self.diary_api.get_class_users()

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

        async for u in self.diary_api.search_people(name, group, school_group, max_page):
            yield u

    async def get_all_peoples(self, max_pages: Optional[int] = None) -> AsyncIterable[Users]:
        """Получить всех школьников и сотрудников школы
        Возвращает итератор объектов словарей вида {"name": "Ivan", "uri": "url"}"""
        if not max_pages:
            max_pages = 100_000
        async for u in self.diary_api.get_all_peoples(max_pages):
            yield u

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

        async for u in self.diary_api.birthdays_near(group, max_pages):
            yield u

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
        return await self.diary_api.calendar_birthdays()

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
        return await self.diary_api.get_diary(period)

    async def close(self):
        await self.diary_api.close()

