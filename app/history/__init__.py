import json
import os
import threading
from datetime import datetime

import cv2
import mss
import numpy as np
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

router = APIRouter(tags=["history"])


RECORDS_DIR = "records"
METADATA_FILE = os.path.join(RECORDS_DIR, "metadata.json")
VIDEO_FPS = 15.0


class RecordActionRequest(BaseModel):
    enable: bool


class DeleteRecordRequest(BaseModel):
    delete: bool


class UpdateRecordRequest(BaseModel):
    title: str


class RecordMetadata(BaseModel):
    rid: int
    title: str
    date: str
    time: str
    duration_seconds: float = 0.0
    file_size_mb: float = 0.0


class ScreenRecorder(object):
    def __init__(self, storage) -> None:
        self._is_recording = False
        self._recording_thread: None | threading.Thread = None
        self._stop_event = threading.Event()
        self.output_filename = ""
        self.start_time = None
        self.storage = storage

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def start(self):
        if self.is_recording:
            print("Already recording")
            return

        self._is_recording = True
        self._stop_event.clear()
        rid = self.storage.get_next_rid()
        self.output_filename = os.path.join(RECORDS_DIR, f"record_{rid}.mp4")
        self.start_time = datetime.now()
        self._recording_thread = threading.Thread(
            target=self._record_loop, args=(rid, self.start_time)
        )
        self._recording_thread.start()
        print(f"Started recording to {self.output_filename}")

        return {"message": "Recording started.", "rid": rid}

    def stop(self):
        if not self._is_recording:
            print("Not currently recording.")
            return

        self._stop_event.set()
        if self._recording_thread:
            self._recording_thread.join()

        self._is_recording = False
        self._recording_thread = None

        print(f"Stopped recording, File saved to {self.output_filename}")
        self.output_filename = ""
        self.start_time = None
        return {"message": "Recording stopped."}

    def _record_loop(self, rid: int, start_time: datetime):
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                out = cv2.VideoWriter(
                    self.output_filename,
                    fourcc,
                    VIDEO_FPS,
                    (monitor["width"], monitor["height"]),
                )
                while not self._stop_event.is_set():
                    img = np.array(sct.grab(monitor))
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    out.write(frame)
                out.release()

                duration = (datetime.now() - start_time).total_seconds()
                file_size = os.path.getsize(self.output_filename) / (1024 * 1024)
                self.storage.add_record(
                    {
                        "rid": rid,
                        "title": f"Recording-{rid}",
                        "date": start_time.strftime("%Y-%m-%d"),
                        "time": start_time.strftime("%H:%M:%S"),
                        "duration_seconds": round(duration, 2),
                        "file_size_mb": round(file_size, 2),
                    }
                )
        except Exception as e:
            print(f"An error occurred during recording: {e}")
        finally:
            cv2.destroyAllWindows()


class StorageManager(object):
    def __init__(self, directory: str, metadata_file: str) -> None:
        self.directory = directory
        self.metadata_file = metadata_file
        self._setup()

    def _setup(self):
        os.makedirs(self.directory, exist_ok=True)
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, "w") as f:
                json.dump([], f)

    def _read_metadata(self) -> list[dict]:
        try:
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_metadata(self, data: list[dict]):
        with open(self.metadata_file, "w") as f:
            json.dump(data, f, indent=4)

    def get_all_records(self) -> list[RecordMetadata]:
        metadata = self._read_metadata()
        return [RecordMetadata(**record) for record in metadata]

    def get_record_by_rid(self, rid: int) -> RecordMetadata | None:
        records = self.get_all_records()
        for record in records:
            if record.rid == rid:
                return record
        return None

    def get_next_rid(self) -> int:
        records = self._read_metadata()
        if not records:
            return 1
        return max(record["rid"] + 1 for record in records)

    def add_record(self, record_data: dict):
        all_records = self._read_metadata()
        all_records.append(record_data)
        self._write_metadata(all_records)

    def update_record_metadata(
        self, rid: int, update_data: dict
    ) -> RecordMetadata | None:
        all_records = self._read_metadata()
        record_found = False
        updated_record_data = None
        for i, record in enumerate(all_records):
            if record["rid"] == rid:
                if update_data.get("title"):
                    record["title"] = update_data["title"]

                all_records[i] = record
                updated_record_data = record
                record_found = True
                break
        if not record_found:
            return None
        self._write_metadata(all_records)
        return RecordMetadata(**updated_record_data) if updated_record_data else None

    def delete_record(self, rid: int) -> bool:
        all_records = self._read_metadata()
        record_to_delete = None
        for record in all_records:
            if record["rid"] == rid:
                record_to_delete = record
                break
        if not record_to_delete:
            return False

        all_records = [r for r in all_records if r["rid"] != rid]
        self._write_metadata(all_records)

        video_path = os.path.join(self.directory, f"record_{rid}.mp4")
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"Deleted video file: {video_path}")
        return True


storage = StorageManager(RECORDS_DIR, METADATA_FILE)
recorder = ScreenRecorder(storage)


@router.get("/hi")
async def hi(name: str = "history") -> str:
    return f"hi, {name}"


@router.get("/status", response_model=bool)
async def get_record_status():
    return recorder.is_recording


@router.post("/record")
async def toggle_record(request: RecordActionRequest):
    if request.enable:
        if recorder.is_recording:
            raise HTTPException(
                status_code=400, detail="A recording session is already in progress."
            )
        return recorder.start()
    else:
        if not recorder.is_recording:
            raise HTTPException(
                status_code=400, detail="No recording is currently in progress to stop."
            )
        return recorder.stop()


@router.get("/records", response_model=list[RecordMetadata])
async def get_all_records_info():
    return storage.get_all_records()


@router.get("/record/{rid}")
async def get_video(rid: int, download: bool = False):
    record_meta = storage.get_record_by_rid(rid)
    if not record_meta:
        raise HTTPException(status_code=404, detail=f"Record with ID {rid} not found.")

    video_path = os.path.join(RECORDS_DIR, f"record_{rid}.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(
            status_code=404, detail=f"Video file for record ID {rid} not found on disk."
        )
    media_type = "application/octet-stream" if download else "video/mp4"
    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="record_{rid}.mp4"'
    return FileResponse(path=video_path, media_type=media_type, headers=headers)


@router.post("/record/{rid}")
async def delete_record(rid: int, request: DeleteRecordRequest):
    if not request.delete:
        return JSONResponse(
            status_code=400,
            content={"detail": "To delete a record, the 'delete' flag must be true."},
        )
    if recorder.is_recording and storage.get_record_by_rid(rid) is None:
        current_rid = int(recorder.output_filename.split("_")[-1].split(".")[0])
        if rid == current_rid:
            raise HTTPException(
                status_code=404,
                detail="Cannot delete a recording that is currently in progress.",
            )
    success = storage.delete_record(rid)
    if not success:
        raise HTTPException(status_code=404, detail=f"Record with ID {rid} not found.")
    return {"message": f"Successfully deleted record {rid}."}


@router.post("/record/{rid}/update", response_model=RecordMetadata)
async def update_record_metadata(rid: int, request: UpdateRecordRequest = Body(...)):
    update_data = request.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400, detail="No update data provided. Please provide a 'title'."
        )
    updated_record = storage.update_record_metadata(rid, update_data)
    if not updated_record:
        raise HTTPException(status_code=404, detail=f"Record with ID {rid} not found.")
    return updated_record
