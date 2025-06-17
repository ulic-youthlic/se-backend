import os
import json

from ..models.video_mata import VideoMetaModel


class VideoRepository(object):
    def __init__(self, directory: str, metadata_file: str) -> None:
        self.directory = directory
        self.metadata_filename = metadata_file
        self.username = "admin"
        self._setup()

    @property
    def metadata_file(self):
        return os.path.join(self.directory, self.username, self.metadata_filename)

    def set_username(self, username):
        self.username = username
        self._setup()

    def _setup(self):
        os.makedirs(os.path.join(self.directory, self.username), exist_ok=True)
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

    def get_all_record_meta(self) -> list[VideoMetaModel]:
        metadata = self._read_metadata()
        return [VideoMetaModel(**record) for record in metadata]

    def get_record_by_rid(self, rid: int) -> VideoMetaModel | None:
        records = self.get_all_record_meta()
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
    ) -> VideoMetaModel | None:
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
        return VideoMetaModel(**updated_record_data) if updated_record_data else None

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

        video_path = self.get_video_path(rid)
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"Deleted video file: {video_path}")
        return True

    def get_video_path(self, rid: int) -> str:
        return os.path.join(self.directory, self.username, f"record_{rid}.mp4")
