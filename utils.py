from datetime import date, timedelta


class Date:
    """класс для сознания свежей даты здесь и сейчас"""
    @staticmethod
    def from_() -> str:
        """сегодняшняя дата в формате "%d.%m.%Y"""
        return date.today().strftime("%d.%m.%Y")

    @staticmethod
    def to(days: int = 10) -> str:
        """сегодняшняя дата + число дней. По умолчанию 10"""
        return (date.today() + timedelta(days=days)).strftime("%d.%m.%Y")

    @staticmethod
    def year() -> str:
        """возвращает текущий год"""
        return date.today().strftime("%Y")

    @staticmethod
    def day() -> int:
        """возвращает текущий день"""
        return date.today().day

    @staticmethod
    def mouth() -> int:
        return date.today().month
