import unittest
from os import getenv

try:
    import dotenv
except (ImportError, ModuleNotFoundError):
    raise ImportError(
        """
Для корректной работы тестов необходимо установить python-dotenv,
создать файл .env и добавить поля:
login=  # логин дневникру
password=  # пароль дневникру
date=  # дата, за которую гарантированно вернёт дневник за неделю
""")

from aiohttp import ClientConnectionError

from dnevnik import Dnevnik
from models import Diary, Users, YearBirthday
from exceptions import PageNotFound

events = []

dotenv.load_dotenv()
login = getenv("login")
password = getenv("password")
date = getenv("date")


class TestBasic(unittest.IsolatedAsyncioTestCase):
    """Тесты на возвращение объектов обычной авторизации
    """
    def setUp(self):
        events.append("setUp")

    async def asyncSetUp(self) -> None:
        self.dnevnik = Dnevnik(login, password)
        try:
            await self.dnevnik.auth()
        except ConnectionError:
            print("Auth error!")
            exit(1)
        events.append("asyncSetUp")

    async def asyncTearDown(self) -> None:
        await self.dnevnik.close()

    async def test_failAuth(self):
        async with Dnevnik("foobar", "qwerty123") as d:
            with self.assertRaises(ClientConnectionError):
                await d.auth()
        self.addAsyncCleanup(self.on_cleanup)

    async def test_getBirthdaysObj(self):
        bdays_calendar = await self.dnevnik.calendar_birthdays()
        self.assertIsInstance(bdays_calendar, YearBirthday)
        self.addAsyncCleanup(self.on_cleanup)

    async def test_getDiaryObj(self):
        diary = await self.dnevnik.get_diary(date)
        self.assertIsInstance(diary, Diary)
        self.addAsyncCleanup(self.on_cleanup)

    async def test_getDiaryEmpty(self):
        with self.assertRaises(PageNotFound):
            await self.dnevnik.get_diary("01.01.2010")
        self.addAsyncCleanup(self.on_cleanup)

    async def test_getClassUsers(self):
        users = await self.dnevnik.get_class_users()
        self.assertIsInstance(users, Users)
        self.addAsyncCleanup(self.on_cleanup)

    async def test_CloseSession(self):
        f = await self.dnevnik.close()
        self.assertIsNone(f)
        with self.assertRaises(RuntimeError):
            await self.dnevnik.calendar_birthdays()

    async def on_cleanup(self):
        events.append("cleanup")


if __name__ == '__main__':
    unittest.main()
