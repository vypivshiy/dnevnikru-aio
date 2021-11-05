from dataclasses import dataclass
from typing import List, Tuple, Iterable

"""Модель взаимодействия с дневником
Diary:
    info: Info
    themes: List[Theme]
    attendances: List[Attendance]
    progress: List[Progress]
    schedules: List[Schedule]
    homeworks: List[Homework]
"""


@dataclass()
class Info:
    """Объект информации о пользователе.

    name: Фио


    school_name: название школы


    class_name: номер класса


    year: учебный год

    date: дата дневника
    """
    name: str
    school_name: str
    class_name: str
    year: str
    date: str

    def __str__(self):
        return f"{self.name} {self.school_name} {self.class_name} {self.year} {self.date}"


@dataclass()
class Homework:
    """Объект домашнего задания

    lesson: предмет


    homework: домашнее задание
    """
    lesson: str
    homework: str

    def __str__(self):
        return f"{self.lesson} {self.homework}"


@dataclass()
class Schedule:
    """Объект расписаний

    day: название дня

    items: кортеж уроков
    """
    day: str
    items: Tuple[str]

    def __str__(self):
        return f"{self.day}\n" + "\n".join([i for i in self.items])

    def __iter__(self):
        return iter(self.items)


@dataclass()
class Progress:
    """Объект успеваемости

    grade: оценка


    type: тип (ответ, самостоятельная, контрольная)


    lesson: название урока
    """
    grade: int
    type: str
    lesson: str

    def __str__(self):
        return f"{self.lesson} - {self.type} {self.grade}"


@dataclass()
class Attendance:
    """Объект посещаемости

    date: дата


    stats: список пропусков/посещений
    """
    date: str
    stats: List[str]

    def __str__(self):
        return f"{self.date} {' '.join([_ for _ in self.stats])}"


@dataclass()
class Theme:
    """тема урока

    name: название урока


    theme: тема урока
    """
    name: str
    theme: str

    def __str__(self):
        return f"{self.name} - {self.theme}"


@dataclass()
class Diary:
    """Объект дневника

    info: Info - информация о пользователе


    themes: List[Theme] - список тем уроков


    attendances: List[Attendance] - список посещаемости


    progress: List[Progress] - список успеваемости


    schedules: List[Schedule] - список расписания


    homeworks: List[Homework] - список домашних заданий
    """
    info: Info
    themes: List[Theme]
    attendances: List[Attendance]
    progress: List[Progress]
    schedules: List[Schedule]
    homeworks: List[Homework]

    def __str__(self):
        themes = "\n".join([_.__str__() for _ in self.themes])
        attendances = "\n".join([_.__str__() for _ in self.attendances])
        progress = "\n".join([_.__str__() for _ in self.progress])
        schedules = "\n".join([_.__str__() for _ in self.schedules])
        homeworks = "\n".join([_.__str__() for _ in self.homeworks])
        return f"""{self.info.__str__()}
{"_"*30}
Themes:
{"_"*30}
{themes}
{"_"*30}
Attendance:
{"_"*30}
{attendances}
{"_"*30}
Progress:
{"_"*30}
{progress}
{"_"*30}
Schedules:
{"_"*30}
{schedules}
{"_"*30}
Homeworks:
{"_"*30}
{homeworks}"""
