from dataclasses import dataclass
from multiprocessing import Process
from typing import Dict


@dataclass
class UserContext(object):
    name: str
    process: Process | None = None


user_contexts: Dict[str, UserContext] = {}
admin_contexts: Dict[str, UserContext] = {}
