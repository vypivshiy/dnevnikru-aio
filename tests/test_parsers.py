import unittest
from asyncio import get_event_loop

from tests.download_html import *
from parsers import Parser, ParserDiary, ParserUsers, ParserBirthdayCalendar
from models import *

"""
Тесты парсеров.
Выгружает актуальные html страницы и проверяет возвращаемые объекты
"""


def setUpModule():
    print("start download html pages")
    loop = get_event_loop()
    loop.run_until_complete(download())
    while loop.is_running():
        pass


def tearDownModule():
    print("delete html pages")
    remove_files()


class TestParsers(unittest.TestCase):
    def test_UserFeed(self):
        html = open_html("userfeed.html")
        profile_id = Parser.parse_profile_id(html)
        group_id = Parser.parse_group_id(html)
        self.assertTrue(group_id.isdigit())
        self.assertTrue(profile_id.isdigit())

    def test_BirthdayCalendar(self):
        html = open_html("bday_calendar.html")
        p = ParserBirthdayCalendar(html)
        calendar = p.create_model()
        self.assertIsInstance(calendar, YearBirthday)
        for day in calendar:
            self.assertIsInstance(day, Day)
            self.assertIsInstance(day.day, int)
            self.assertIsInstance(day.count, int)
            self.assertIsInstance(day.month, str)
            self.assertIsInstance(day.url, str)
            self.assertTrue(day.url.startswith("http"))
            self.assertIsInstance(day.month_int(), int)

    def test_BirthdayNear(self):
        html = open_html("bday_near.html")
        p = ParserUsers(html)
        users = p.create_model()
        self.assertIsInstance(users, Users)
        for u in users:
            self.assertIsInstance(u.url, str)
            self.assertTrue(u.url.startswith("http"))
            self.assertIsInstance(u.full_name, str)

    def test_Diary(self):
        html = open_html("diary.html")
        p = ParserDiary(html)
        diary = p.gen_model
        self.assertIsInstance(diary, Diary)
        self.assertIsInstance(diary.info, Info)
        self.assertIsInstance(diary.info.date, str)
        self.assertIsInstance(diary.info.name, str)

        theme = diary.themes[0]
        self.assertIsInstance(theme, Theme)

        attendance = diary.attendances[0]
        self.assertIsInstance(attendance, Attendance)

        progress = diary.progress[0]
        self.assertIsInstance(progress, Progress)

        homework = diary.homeworks[0]
        self.assertIsInstance(homework, Homework)

        schedule = diary.schedules[0]
        self.assertIsInstance(schedule, Schedule)

    def test_parseUsers(self):
        html = open_html("class_users.html")
        p = ParserUsers(html)
        users = p.create_model()
        self.assertIsInstance(users, Users)
        for u in users:
            self.assertIsInstance(u.url, str)
            self.assertIsInstance(u.full_name, str)

        html = open_html("school.html")
        p = ParserUsers(html)
        users = p.create_model()
        self.assertIsInstance(users, Users)
        for u in users:
            self.assertIsInstance(u.url, str)
            self.assertIsInstance(u.full_name, str)


if __name__ == '__main__':
    unittest.main()
