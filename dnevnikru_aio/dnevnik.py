from datetime import date
from typing import AsyncIterable, Optional

from .types import Diary, YearBirthday, Users
from .session import DiaryAPI

__version__ = "1.0"


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
        """Метод авторизации через dnevnik.ru **не через госулуги**

        :raise: ClientConnectionError при неудачной авторизации
        :return: True если авторизация прошла успешно
        """
        return await self.diary_api.auth()

    async def get_class_users(self) -> Users:
        """Метод получения всех одноклассников из своего класса

        :return: Users object
        :rtype: Users
        :example:
        >>> users = await Dnevnik.get_class_users()
        >>> isinstance(users.count, int)
        True
        """
        return await self.diary_api.get_class_users()

    async def search_people(self, name: str = "", group: str = "all",
                            school_group: str = "", max_page: Optional[int] = None) -> AsyncIterable[Users]:
        """Поиск людей из всей школы. Если дополнительные параметры не переданы, то вернёт всех пользователей.
        Если ничего не найдёт, вернёт пустой итератор

        Доступные категории групп: "all", "students", "staff", "administrators", "teachers", "management", "director"

        :param str name: поиск по Имени/Фамилии/Отчеству по отдельности или все вместе
        :param str group: поиск по категории. По умолчанию или при некорректном вводе устанавливается "all".
        :param str school_group: поиск по номеру класса
        :param int max_page: максимальное число итераций страниц. По умолчанию обходит все
        :return: Итератор объектов Users
        :rtype: AsyncIterable[Users]

        :example:
        >>> async for users in Dnevnik.search_people(name="Олег", max_page=3):
        ...     print(users.count)
        ...     for user in users:
        ...         print(user.full_name)
        """
        available_groups = ["all", "students", "staff", "administrators", "teachers", "management", "director"]
        if group not in available_groups:
            group = "all"

        if not max_page:
            max_page = 100_000

        async for users in self.diary_api.search_people(name, group, school_group, max_page):
            yield users

    async def get_all_peoples(self, max_pages: Optional[int] = None) -> AsyncIterable[Users]:
        """Wrapper метода search_people

        :param int max_pages: Максимально число страниц для итерации. По умолчанию обходит все.
        :return: Возвращает итератор объектов Users
        :rtype: AsyncIterable[Users]
        """
        if not max_pages:
            max_pages = 100_000
        async for u in self.diary_api.get_all_peoples(max_pages):
            yield u

    async def birthdays_near(self, group: str = "all", max_pages: Optional[int] = None) -> AsyncIterable[Users]:
        """Поиск людей, у кого в ближайшие 2 недели будет день рождения. (Дату ДР не возвращает)

        Доступные категории групп: "all", "students", "staff", "class"

        :param str group: тип поиска подгруппы людей. По умолчанию "all"
        :param int max_pages: максимальное число страниц для итерации. По умолчанию все.
        :return: Возвращает итератор объектов Users
        :rtype: AsyncIterable[Users]
        """
        available_groups = ["all", "students", "staff", "class"]
        if group not in available_groups:
            group = "all"
        if not max_pages:
            max_pages = 100

        async for u in self.diary_api.birthdays_near(group, max_pages):
            yield u

    async def calendar_birthdays(self) -> YearBirthday:
        """Возвращает весь календарь с числом именинников за каждый день

        :return: объект Календаря с именинниками
        :rtype: YearBirthday

        :example:
        >>> calendar = await Dnevnik.calendar_birthdays()
        >>> print(calendar.days)
        """
        return await self.diary_api.calendar_birthdays()

    async def get_diary(self, period: str = date.today().strftime("%d.%m.%Y")) -> Diary:
        """Получение дневника за неделю

        :param str period: Период получения дневника в формате "%d.%m.%Y". По умолчанию устанавливает на сегодня.
        :return: Объект дневника
        :rtype: Diary

        :example:

        >>> diary = await Dnevnik.get_diary(period="03.09.2077")
        >>> print(diary.info)  # информация об ученике
        >>> print(diary.themes)  # учебный план
        >>> print(diary.progress)  # успеваемость
        >>> print(diary.homeworks)  # домашние задания
        >>> print(diary.schedules)  # расписание
        >>> print(diary.attendances)  # посещаемость
        """
        return await self.diary_api.get_diary(period)

    async def close(self):
        """Закрытие сессии"""
        await self.diary_api.close()
