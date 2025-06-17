from pydantic import BaseModel


class GameToggleRequest(BaseModel):
    enable: bool


class GameToggleResponse(BaseModel):
    success: bool


class GameStatusResponse(BaseModel):
    running: bool
