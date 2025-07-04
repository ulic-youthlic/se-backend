from app.control.game_log import GameLog
from app.control.user import User
from app.entity.repositories.log import LogReposity
from app.entity.repositories.user import UserRepository, database
from app.control.game import GameManager
from app.control.recorder import Recorder
from app.entity.repositories.video import VideoRepository

recorder = Recorder(VideoRepository("records", "meta.json"))
game_manager = GameManager()


def get_user_controller():
    return User(UserRepository(database))


def get_game_log_controller(username: str):
    return GameLog(LogReposity(username))


def get_game_manager_controller(username: str = "admin"):
    game_manager.set_username(username)
    return game_manager


def get_recorder_controller(username: str = "admin"):
    recorder.video_repo.set_username(username)
    return recorder
