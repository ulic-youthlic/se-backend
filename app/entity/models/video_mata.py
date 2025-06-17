from pydantic import BaseModel


class VideoMetaModel(BaseModel):
    rid: int
    title: str
    date: str
    time: str
    duration_seconds: float
    file_size_mb: float
