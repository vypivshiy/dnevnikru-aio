from dataclasses import dataclass
from typing import List, Iterable


@dataclass()
class User:
    """Объект пользователя

    full_name - имя пользователя


    url - ссылка на профиль (если пользователь зарегистрирован)

    """
    full_name: str
    url: str


@dataclass()
class Users:
    """Хранилище Объектов пользователей

    count - количество пользователей


    items - список объектов User

    """
    count: int
    items: List[User]

    def __iter__(self) -> Iterable[User]:
        return iter(self.items)
