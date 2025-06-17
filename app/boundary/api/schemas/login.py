from pydantic import BaseModel


class LoginRegisterRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class LoginRegisterResponse(BaseModel):
    code: int
    message: str


class LoginLoginRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class LoginLoginResponse(BaseModel):
    code: int
    message: str
