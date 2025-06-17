from app.entity.models.user import UserModel
from app.entity.repositories.user import UserRepository


class User(object):
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate_user(self, username: str, password: str, is_admin: bool) -> bool:
        user = self.user_repo.get_user_by_name(username=username)
        if user is not None and user.password == password and user.is_admin == is_admin:
            return True
        else:
            return False

    def register_user(self, username: str, password: str, is_admin: bool) -> bool:
        if self.user_repo.get_user_by_name(username=username) is not None:
            return False
        self.user_repo.create_user(
            UserModel(username=username, password=password, is_admin=is_admin)
        )
        return True
