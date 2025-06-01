from typing import Dict

from pydantic import BaseModel, RootModel


class User(BaseModel):
    password: str


class UserDatabase(RootModel):
    root: Dict[str, User]


with open("user.json", "r") as file:
    USERS = UserDatabase.model_validate_json(file.read(), strict=True).model_dump()

with open("admin.json", "r") as file:
    ADMINS = UserDatabase.model_validate_json(file.read(), strict=True).model_dump()

HOST = "127.0.0.1"
PORT = 5000
LOG_FILE = "log.txt"
