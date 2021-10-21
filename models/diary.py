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
    name: str
    school_name: str
    class_name: str
    year: str
    date: str

    def __str__(self):
        return f"{self.name} {self.school_name} {self.class_name} {self.year} {self.date}"


@dataclass()
class Homework:
    lesson: str
    homework: str

    def __str__(self):
        return f"{self.lesson} {self.homework}"


@dataclass()
class Schedule:
    day: str
    items: Tuple[str]

    def __str__(self):
        return f"{self.day}\n" + "\n".join([i for i in self.items])


@dataclass()
class Progress:
    grade: int
    type: str
    lesson: str

    def __str__(self):
        return f"{self.lesson} - {self.type} {self.grade}"


@dataclass()
class Attendance:
    date: str
    stats: List[str]

    def __str__(self):
        return f"{self.date} {' '.join([_ for _ in self.stats])}"


@dataclass()
class Theme:
    """тема урока"""
    name: str
    theme: str

    def __str__(self):
        return f"{self.name} - {self.theme}"


@dataclass()
class Diary:
    """Модель дневника"""
    info: Info
    themes: List[Theme]
    attendances: List[Attendance]
    progress: List[Progress]
    schedules: List[Schedule]
    homeworks: List[Homework]

    @property
    def get_homework(self) -> Iterable[Homework]:
        hw: Homework
        for hw in self.homeworks:
            yield hw

    @property
    def get_schedules(self) -> Iterable[Schedule]:
        sc: Schedule
        for sc in self.schedules:
            yield sc

    @property
    def get_attendances(self):
        for at in self.attendances:
            yield at

    @property
    def get_progress(self) -> Iterable[Progress]:
        pr: Progress
        for pr in self.progress:
            yield pr

    @property
    def get_themes(self) -> Iterable[Theme]:
        th: Theme
        for th in self.themes:
            yield th

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

