import multiprocessing
import subprocess
import sys
import threading

from half_life2_agent.test_development.path_planning_based_on_vision.main_for_test_slam_with_decision_tree_and_nn import (
    GameBot,
)


class GameManager(object):
    def __init__(self):
        self._game_process = None
        self._support_process = None
        self._support_enabled = False

    def _start_game(self) -> bool:
        command = [sys.executable, "game/CG/panda3D3/main.py"]
        try:
            self._game_process = subprocess.Popen(command)
            watcher = threading.Thread(
                target=lambda: self._watch_process(), args=(), daemon=True
            )
            watcher.start()
            return True
        except Exception as e:
            print(f"{e}")
            return False

    def _stop_game(self) -> bool:
        if self._game_process is not None:
            pid = self._game_process.pid
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(pid)],
                    check=True,
                    capture_output=True,
                )
                self._game_process = None
                return True
            except subprocess.CalledProcessError as e:
                if "not found" in e.stderr.decode(errors="ignore"):
                    self._game_process = None
                    return True
                else:
                    return False
            except Exception as e:
                print(e)
                return False
        return False

    def _watch_process(self):
        if self._game_process is not None:
            self._game_process.wait()
            self._stop_support()
        if self._game_process is not None:
            self._game_process = None

    def _start_support(self):
        def start():
            bot = GameBot()
            bot.run()

        process = multiprocessing.Process(target=start)
        process.start()
        self._support_process = process
        self._support_enabled = True

    def _stop_support(self):
        if self._support_process is not None and self._support_process.is_alive():
            self._support_process.terminate()
            self._support_process.join()
            self._support_process = None
        self._support_enabled = False

    @property
    def support_enabled(self):
        return self._support_enabled

    @property
    def game_running(self):
        return self._game_process is not None and self._game_process.poll() is None

    def set_support_status(self, new_status: bool):
        if new_status:
            if self.support_enabled or not self.game_running:
                return False
            else:
                self._start_support()
                return True
        else:
            if self.support_enabled:
                self._stop_support()
                return True
            else:
                return False

    def set_game_status(self, new_status: bool):
        if new_status:
            if self.game_running:
                return False
            return self._start_game()
        else:
            if not self.game_running:
                return False
            return self._stop_game()
