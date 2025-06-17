from typing import List

from pydantic import BaseModel, RootModel


class HistoryRecordingStatusResponse(RootModel):
    root: bool


class HistoryToggleRecordRequest(BaseModel):
    enable: bool


class HistoryToggleRecordResponse(BaseModel):
    message: str


class HistoryRecordInfo(BaseModel):
    rid: int
    title: str
    date: str
    time: str
    duration_seconds: float = 0.0
    file_size_mb: float = 0.0


class HistoryAllRecordInfosResponse(RootModel):
    root: List[HistoryRecordInfo]


class HistoryVideoRequest(RootModel):
    root: bool


class HistoryDeleteVideoRequest(BaseModel):
    delete: bool


class HistoryDeleteVideoResponse(BaseModel):
    message: str


class HistoryUpdateMetadataRequest(BaseModel):
    title: str


class HistoryUpdateMetadataResponse(BaseModel):
    rid: int
    title: str
    date: str
    time: str
    duration_seconds: float = 0.0
    file_size_mb: float = 0.0
