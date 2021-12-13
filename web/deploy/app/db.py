from typing import List, Optional
from pydantic import BaseModel
from dataclasses import dataclass
import random
import string


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass
class User:
    username: str
    password: str
    notes: List[str]
    admin: bool = False


def get_rnd(k=10, alp=string.ascii_letters) -> str:
    return "".join(random.choices(alp, k=k))


class DB(metaclass=Singleton):
    users: List[User]

    def __init__(self) -> None:
        self.users = [
            User(
                "admin",
                "p35vbo7tco4n5yuci34uc5fi3t5c",
                [],
                True,
            )
        ]

    async def find(self, login: str) -> Optional[User]:
        for user in self.users:
            if user.username == login:
                return user
        return None

    async def register(self, login: str, password: str) -> User:
        user = User(
            username=login,
            password=password,
            notes=[],
        )
        self.users.append(user)
        return user
