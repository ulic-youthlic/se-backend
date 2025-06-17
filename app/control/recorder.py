import os
import threading
from datetime import datetime

import cv2
import mss
import numpy as np

from app.entity.repositories.video import VideoRepository


class Recorder(object):
    def __init__(self, video_repo: VideoRepository):
        self._is_recording = False
        self._recording_thread: None | threading.Thread = None
        self._stop_event = threading.Event()
        self.output_filename = ""
        self.start_time = None
        self.video_repo = video_repo

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def _start(self) -> bool:
        if self.is_recording:
            print("Already recording")
            return False

        self._is_recording = True
        self._stop_event.clear()
        rid = self.video_repo.get_next_rid()
        self.output_filename = self.video_repo.get_video_path(rid)
        self.start_time = datetime.now()
        self._recording_thread = threading.Thread(
            target=self._record_loop, args=(rid, self.start_time)
        )
        self._recording_thread.start()
        print(f"Started recording to {self.output_filename}")

        return True

    def _stop(self) -> bool:
        if not self._is_recording:
            print("Not currently recording.")
            return False

        self._stop_event.set()
        if self._recording_thread:
            self._recording_thread.join()

        self._is_recording = False
        self._recording_thread = None

        print(f"Stopped recording, File saved to {self.output_filename}")
        self.output_filename = ""
        self.start_time = None
        return True

    def _record_loop(self, rid: int, start_time: datetime):
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                out = cv2.VideoWriter(
                    self.output_filename,
                    fourcc,
                    15.0,
                    (monitor["width"], monitor["height"]),
                )
                while not self._stop_event.is_set():
                    img = np.array(sct.grab(monitor))
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    out.write(frame)
                out.release()

                duration = (datetime.now() - start_time).total_seconds()
                file_size = os.path.getsize(self.output_filename) / (1024 * 1024)
                self.video_repo.add_record(
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

    def set(self, new_status: bool) -> bool:
        return self._start() if new_status else self._stop()
