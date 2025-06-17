import os
import re

from ..models.log import LogEntry

LOG_FILE = "log.txt"


class LogReposity(object):
    def __init__(self, username: str):
        try:
            with open(os.path.join("log", username, LOG_FILE), "r") as f:
                lines = f.readlines()
            self.log = list(map(self._parse_line, lines))
        except FileNotFoundError:
            self.log = []



    @staticmethod
    def _parse_line(line: str) -> LogEntry:
        pattern = r"\[(.*?)\]\s+Score:\s+(\d+),\s+Time:\s+([\d:]+),\s+Kills:\s+(\d+),\s+Cubes:\s+(\d+)"
        match = re.match(pattern, line)
        assert match is not None
        timestamp_str = match.group(1)
        score = int(match.group(2))
        time_str = match.group(3)
        kills = int(match.group(4))
        cubes = int(match.group(5))

        return LogEntry(
            timestamp=timestamp_str,
            score=score,
            time=time_str,
            kills=kills,
            cubes=cubes,
        )
