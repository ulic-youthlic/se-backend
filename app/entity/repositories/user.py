import sqlite3

from ..models.user import UserModel

DATABASE_URL = "user.db"


class DataBase(object):
    def __init__(self):
        self._conn = sqlite3.connect(DATABASE_URL)
        self._conn.row_factory = sqlite3.Row

    @property
    def conn(self):
        return self._conn


database = DataBase()


def init_db():
    with database.conn as conn:
        conn.execute("""
                         CREATE TABLE IF NOT EXISTS users (
                             username TEXT NOT NULL PRIMARY KEY,
                             password TEXT NOT NULL,
                             is_admin BOOLEAN NOT NULL DEFAULT 0
                         );
                     """)
        conn.commit()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
        if cursor.fetchone() is None:
            password = "111111"
            cursor.execute(
                "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                ("admin", password, True),
            )
            conn.commit()
            print(f"Default admin user 'admin' with password '{password}' created.")


class UserRepository(object):
    def __init__(self, db: DataBase):
        self.db = db

    def get_user_by_name(self, username: str):
        with self.db.conn as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user_row = cursor.fetchone()
            if user_row is not None:
                return UserModel(**dict(user_row))
            else:
                return None

    def create_user(self, user: UserModel):
        with self.db.conn as conn:
            conn.execute(
                "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                (user.username, user.password, user.is_admin),
            )
            conn.commit()
