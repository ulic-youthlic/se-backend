from pydantic import BaseModel


class UserModel(BaseModel):
    username: str
    password: str
    is_admin: bool
