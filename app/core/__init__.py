import multiprocessing

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
