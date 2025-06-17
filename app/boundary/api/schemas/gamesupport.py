from pydantic import BaseModel


class GameSupportToggleRequest(BaseModel):
    username: str = "admin"
    enable: bool


class GameSupportToggleResponse(BaseModel):
    success: bool


class GameSupportStatusResponse(BaseModel):
    enable: bool
