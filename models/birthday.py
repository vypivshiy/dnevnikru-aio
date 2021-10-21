from dataclasses import dataclass
from typing import List


@dataclass()
class Day:
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

    def month_int(self) -> int:
        return self.__MONTH.get(self.month)


@dataclass()
class YearBirthday:
    """Модель календаря именинников"""
    days: List[Day]

