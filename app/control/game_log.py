from typing import List
from app.entity.models.log import LogEntry
from app.entity.repositories.log import LogReposity


class GameLog(object):
    def __init__(self, log_repo: LogReposity):
        self.log_repo = log_repo

    def get_all_info(self) -> List[LogEntry]:
        return self.log_repo.log
