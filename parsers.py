import re

from bs4 import BeautifulSoup

from models import *


class Parser:

    @staticmethod
    def parse_group_id(page: str) -> str:
        """Возвращает id класса, в котором находится авторизованный пользователь"""
        return re.findall(r"https://schools\.dnevnik\.ru/class.aspx\?class=(\d+)", page)[0]

    @staticmethod
    def parse_profile_id(page: str) -> str:
        """Возвращает id профиля"""
        return re.findall(r'"personId":"(\d+)"', page)[0]



class ParserDiary:
    # status patterns
    PATTERN_STATS = dict(name="h5", class_="h5 h5_bold")
    # элементы строки
    LINES = dict(name="li", class_="current-progress-list__item")
    NAME = dict(name="b")
    VAL = dict(name="p")
    VAL_2 = dict(name="p", class_="paragraph paragraph_no-margin paragraph_inline")
    # темы занятий
    PATTERN_THEME = dict(name="div", class_="current-progress-themes")
    # посещаемость
    PATTERN_ATTENDANCE = dict(name="div", class_="current-progress-attendance")
    # успеваемость
    PATTERN_PROGRESS = dict(name="div", class_="current-progress-marks")
    # расписание
    PATTERN_SCHEDULE = dict(name="div", class_="current-progress-schedule")
    SCHEDULE_LINE = dict(name="li", class_="current-progress-schedule__item")
    DAY = dict(name="div", class_="current-progress-schedule__day-title")
    LESSONS = dict(name="li", class_="current-progress-lessons__item")
    # домашка
    PATTERN_HOMEWORK = dict(name="div", class_="current-progress-homeworks")
    # пустой паттерн
    PATTERN_EMPTY = dict(name="div", class_="progress__empty-block")

    def __init__(self, page: str):
        """Парсер информации по эндпоинту https://dnevnik.ru/currentprogress/result"""
        self.soup = BeautifulSoup(page, "lxml")

    @property
    def parse_info(self) -> tuple:
        """Получить имя и статус авторизованного пользователя"""
        name, school_name, class_name, year, date = self.soup.find(**self.PATTERN_STATS).get_text(strip=True).split(",")
        return name, school_name, class_name, year, date

    @property
    def parse_themes(self) -> tuple:
        """парсер тем занятий"""
        themes = self.soup.find(**self.PATTERN_THEME).find_all(**self.LINES)
        for line in themes:
            name = line.find(**self.NAME).get_text(strip=True)
            val = line.find(**self.VAL).get_text(strip=True)
            yield name, val

    @property
    def parse_attendance(self) -> tuple:
        """Парсер посещаемости"""
        attendance = self.soup.find(**self.PATTERN_ATTENDANCE).find_all(**self.LINES)
        if attendance:
            for line in attendance:
                names = line.find_all(**self.NAME)
                name, val = [n.get_text() for n in names]
                yield name, val
        else:
            yield "", []

    @property
    def parse_progress(self) -> tuple:
        """Парсер прогресса"""
        progress = self.soup.find(**self.PATTERN_PROGRESS).find_all(**self.LINES)
        for line in progress:
            names = line.find_all(**self.NAME)
            name, val = [n.get_text() for n in names]
            type_ = line.find(**self.VAL_2).get_text()
            yield name, type_, val

    @property
    def parse_schedule(self) -> tuple:
        """Парсер расписаний"""
        schedule = self.soup.find(**self.PATTERN_SCHEDULE).find_all(**self.SCHEDULE_LINE)
        if schedule:
            for line in schedule:
                day = line.find(**self.DAY)
                lessons = line.find_all(**self.LESSONS)
                if lessons:
                    lessons = tuple([lesson.get_text(strip=True) for lesson in lessons])
                day = day.get_text(strip=True)
                yield day, lessons
        else:
            yield []

    @property
    def parse_homework(self) -> tuple:
        """Парсер домашних заданий"""
        homework = self.soup.find(**self.PATTERN_HOMEWORK).find_all(**self.LINES)
        if homework:
            for line in homework:
                lesson_name = line.find(**self.NAME).get_text()
                lesson_homework = line.find(**self.VAL_2).get_text()
                yield lesson_name, lesson_homework
        else:
            yield []

    def __is_empty(self, soup_: BeautifulSoup) -> bool:
        """TODO возвращает False, если вернёт пустой элемент списка"""
        return False if soup_.find(**self.PATTERN_EMPTY) else True

    def _create_struct(self):
        """Метод создания структуры основной информации"""
        info = Info(*self.parse_info)
        themes = []
        attendances = []
        progress = []
        homeworks = []
        schedules = []

        for name, val in self.parse_themes:
            t = Theme(name=name, theme=val)
            themes.append(t)
        for name, vals in self.parse_attendance:
            a = Attendance(name, vals)
            attendances.append(a)
        for ball, type_, lesson in self.parse_progress:
            p = Progress(ball, type_, lesson)
            progress.append(p)
        for day_name, lessons in self.parse_schedule:
            sc = Schedule(day_name, lessons)
            schedules.append(sc)
        for name, work in self.parse_homework:
            hw = Homework(name, work)
            homeworks.append(hw)
        return Diary(info=info, themes=themes,
                     attendances=attendances, progress=progress,
                     schedules=schedules, homeworks=homeworks
                     )

    @property
    def gen_model(self) -> Diary:
        return self._create_struct()


class ParserBirthdayCalendar:
    # календарь
    PATTERN_CALENDAR = {"name": "table", "class_": "calendar"}
    # месяц
    PATTERN_MONTH = {"name": "caption"}
    # ссылка + число именинников
    PATTERN_COUNT = {"name": "a"}

    def __init__(self, page: str):
        self.soup = BeautifulSoup(page, "lxml")

    def parse(self) -> dict:
        calendar_rows = self.soup.find_all(**self.PATTERN_CALENDAR)
        days = dict()
        for cal_row in calendar_rows:
            month = cal_row.find(**self.PATTERN_MONTH).get_text(strip=True)  # месяц
            rows = cal_row.find_all(**self.PATTERN_COUNT)  # строка с ссылкой и числом именинников
            days[month] = []
            for row in rows:
                day = row.get_text(strip=True)
                # число именинников
                count = row["title"].split(": ")[1] if "В этот день нет дней рождения" not in row["title"] else 0
                # ссылка
                url = row["href"]
                birthday = dict(count=int(count), day=int(day), url=url)
                days[month].append(birthday)
        return days

    def create_model(self) -> YearBirthday:
        calendar_ = self.parse()
        days_models = []
        for month, days in calendar_.items():
            for day in days:
                d = Day(count=day["count"], day=day["day"], url=day["url"], month=month)
                days_models.append(d)
        return YearBirthday(days=days_models)


class ParserUsers:
    """Парсер пользователей"""
    # основная таблица
    PATTERN_TABLE = {"name": "table", "class_": "people grid"}
    # строка таблицы
    PATTERN_ROW = {"name": "td", "class_": "tdName"}
    # строка с пользователем
    PATTERN_USER = {"class_": "u"}
    # количество всех найденных пользователей
    PATTERN_COUNT = {"name": "p", "class_": "found"}

    # парсер числа именниников

    def __init__(self, page: str):
        self.soup = BeautifulSoup(page, "lxml")

    def parse(self):
        count = self.soup.find(**self.PATTERN_COUNT)
        count = re.findall(r"(\d+)", count.get_text(strip=True)) if count else None
        if count:
            count = int(count[0])
            users = dict(count=int(count), users=[])
            rows = self.soup.find(**self.PATTERN_TABLE).find_all(**self.PATTERN_ROW)
            for row in rows:
                row = row.find(**self.PATTERN_USER)
                name = row.get_text(strip=True)
                url = row.get("href", "")
                users["users"].append(dict(name=name, url=url))
            return users
        else:
            return []

    def create_model(self):
        users = self.parse()
        users_list = []
        if users:
            for user in users["users"]:
                users_list.append(User(full_name=user["name"], url=user["url"]))
            return Users(items=users_list, count=users["count"])
        else:
            return Users(items=[], count=0)
