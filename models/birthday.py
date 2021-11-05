from dataclasses import dataclass
from typing import List, Iterable


@dataclass()
class Day:
    """Объект дня с именинниками

    count: int - число именинников


    day: int - номер дня


    month: str - название месяца


    url: str - ссылка на эту дату


    month_int: int - номер месяца
    """
    __MONTH = {
        "Январь": 1,
        "Февраль": 2,
        "Март": 3,
        "Апрель": 4,
        "Май": 5,
        "Июнь": 6,
        "Июль": 7,
        "Август": 8,
        "Сентябрь": 9,
        "Октябрь": 10,
        "Ноябрь": 11,
        "Декабрь": 12,
    }
    count: int
    day: int
    month: str
    url: str

    @property
    def month_int(self) -> int:
        return self.__MONTH.get(self.month)


@dataclass()
class YearBirthday:
    """Модель календаря именинников

    days: List[Day] - список объектов Day
    """
    days: List[Day]

    def __iter__(self) -> Iterable[Day]:
        return iter(self.days)
