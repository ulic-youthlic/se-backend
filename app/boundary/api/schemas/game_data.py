from typing import List

from pydantic import BaseModel


class GameRecord(BaseModel):
    timestamp: str
    score: int
    time: str
    kills: int
    cubes: int


class GameDataInfoResponse(BaseModel):
    success: bool
    message: str
    records: List[GameRecord]
