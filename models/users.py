from dataclasses import dataclass
from typing import List, Iterable


@dataclass()
class User:
    full_name: str
    url: str


@dataclass()
class Users:
    count: int
    items: List[User]

    def __iter__(self) -> Iterable[User]:
        return iter(self.items)
