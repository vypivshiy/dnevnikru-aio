from datetime import date, timedelta


class Date:
    """
    Класс сознания свежей даты.
    """
    @staticmethod
    def from_() -> str:
        """
        :return: текущая дата в формате "%d.%m.%Y
        """
        return date.today().strftime("%d.%m.%Y")

    @staticmethod
    def to(days: int = 10) -> str:
        """
        :param days: сколько дней прибавить к сегодняшней дате. По умолчанию 10
        :return: дата + число дней
        """
        return (date.today() + timedelta(days=days)).strftime("%d.%m.%Y")

    @staticmethod
    def year() -> int:
        """
        :return: текущий год
        """
        return int(date.today().strftime("%Y"))

    @staticmethod
    def day() -> int:
        """
        :return: текущий день
        """
        return date.today().day

    @staticmethod
    def mouth() -> int:
        """

        :return: текущий месяц
        """
        return date.today().month
