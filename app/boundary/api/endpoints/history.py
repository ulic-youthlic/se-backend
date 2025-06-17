import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import FileResponse

from app.boundary.api.schemas.history import (
    HistoryAllRecordInfosResponse,
    HistoryDeleteVideoRequest,
    HistoryDeleteVideoResponse,
    HistoryRecordInfo,
    HistoryRecordingStatusResponse,
    HistoryToggleRecordRequest,
    HistoryToggleRecordResponse,
    HistoryUpdateMetadataRequest,
    HistoryUpdateMetadataResponse,
    HistoryVideoRequest,
)
from app.boundary.deps import get_recorder_controller
from app.control.recorder import Recorder

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/hi")
async def hi(name: str = "history") -> str:
    return f"hi, {name}"


@router.get("/status", response_model=HistoryRecordingStatusResponse)
async def recording_status(
    controller: Annotated[Recorder, Depends(get_recorder_controller)],
):
    return HistoryRecordingStatusResponse(controller.is_recording)


@router.post("/record", response_model=HistoryToggleRecordResponse)
async def toggle_record(
    enable: HistoryToggleRecordRequest,
    controller: Annotated[Recorder, Depends(get_recorder_controller)],
):
    if not controller.set(new_status=enable.enable):
        raise HTTPException(status_code=400, detail="Set recording status failed.")
    return HistoryToggleRecordResponse(message="Change recording status successfully.")


@router.get("/records", response_model=HistoryAllRecordInfosResponse)
async def all_records_info(
    controller: Annotated[Recorder, Depends(get_recorder_controller)],
):
    return HistoryAllRecordInfosResponse(
        [
            HistoryRecordInfo(**dict(i))
            for i in controller.video_repo.get_all_record_meta()
        ]
    )


@router.get("/record/{rid}")
async def video(
    rid: int,
    controller: Annotated[Recorder, Depends(get_recorder_controller)],
    download: HistoryVideoRequest = HistoryVideoRequest(True),
):
    record_meta = controller.video_repo.get_record_by_rid(rid)
    if not record_meta:
        raise HTTPException(status_code=404, detail=f"Record with ID {rid} not found.")
    video_path = controller.video_repo.get_video_path(rid)
    if not os.path.exists(video_path):
        raise HTTPException(
            status_code=404, detail=f"Video file for record ID {rid} not found on disk."
        )
    media_type = "application/octet-stream" if download.root else "video/mp4"
    headers = {}
    if download.root:
        headers["Content-Disposition"] = f'attachment; filename="record_{rid}.mp4"'
    return FileResponse(path=video_path, media_type=media_type, headers=headers)


@router.post("/record/{rid}", response_model=HistoryDeleteVideoResponse)
async def delete_record(
    rid: int,
    request: HistoryDeleteVideoRequest,
    controller: Annotated[Recorder, Depends(get_recorder_controller)],
):
    if not request.delete:
        raise HTTPException(
            status_code=400,
            detail="To delete a record, the 'delete' flag must be true.",
        )
    if not controller.video_repo.delete_record(rid):
        raise HTTPException(status_code=404, detail=f"Record with ID {rid} not found.")
    return HistoryDeleteVideoResponse(message=f"Successfully deleted record {rid}.")


@router.post("/record/{rid}/update", response_model=HistoryUpdateMetadataResponse)
async def update_record_metadata(
    rid: int,
    request: HistoryUpdateMetadataRequest,
    controller: Annotated[Recorder, Depends(get_recorder_controller)],
):
    updated_record = controller.video_repo.update_record_metadata(
        rid, request.model_dump(exclude_unset=True)
    )
    if updated_record is None:
        raise HTTPException(
            status_code=400, detail="No update data provided. Please provide a 'title'."
        )
    return HistoryUpdateMetadataResponse(**dict(updated_record))
