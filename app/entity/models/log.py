from pydantic import BaseModel


class LogEntry(BaseModel):
    timestamp: str
    score: int
    time: str
    kills: int
    cubes: int
