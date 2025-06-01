import multiprocessing
import re
from datetime import datetime

from app.config import LOG_FILE

from half_life2_agent.test_development.path_planning_based_on_vision.main_for_test import (
    GameBot,
)


def start():
    bot = GameBot()
    bot.run()


def launch() -> multiprocessing.Process:
    process = multiprocessing.Process(target=start)
    process.start()
    return process


def teminate(process: multiprocessing.Process):
    if process.is_alive():
        process.terminate()
        process.join()


def parse_line(line: str):
    pattern = r"\[(.*?)\]\s+Score:\s+(\d+),\s+Time:\s+([\d:]+),\s+Kills:\s+(\d+),\s+Cubes:\s+(\d+)"
    match = re.match(pattern, line)
    assert match is not None
    timestamp_str = match.group(1)
    score = int(match.group(2))
    time_str = match.group(3)
    kills = int(match.group(4))
    cubes = int(match.group(5))

    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

    return {
        "timestamp": timestamp,
        "score": score,
        "time": time_str,
        "kills": kills,
        "cubes": cubes,
    }


def meta():
    with open(LOG_FILE, "r") as f:
        line = f.readlines()[-1]
        info = parse_line(line)
    return info
