import psycopg2
from functools import wraps
#my libs
from utils import format_timestamp


class DbhResponse:
    code: int
    data: any
    def __init__(self, code, data):
        self.code = code
        self.data = data

    def valid(self):
        return self.code == 1

class DatabaseHandler:
    def __init__(self, app_logger, dbname='ChatAppDB', user='admin', password='admin', host='db', port='5432'):
        self.app_logger = app_logger
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self._connection = None

    def connect(self):
        if self._connection is None:
            # Connect to the PostgreSQL database with custom parameters
            self._connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )

    def disconnect(self):
        if self._connection is not None:
            # Close the database connection
            self._connection.close()
            self._connection = None

    def decorator_connection(func) -> callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> DbhResponse:
            try:
                self.app_logger.info("Call db")
                self.connect()  # Connect before executing the function
                result = func(self, *args, **kwargs)
                return DbhResponse(1, result)
            except psycopg2.Error as e:
                self.app_logger.info("Database connection error:", e.pgcode)
                return DbhResponse(0, None)
            except ValueError as ve:
                self.app_logger.info("ValueError occurred:", ve)
                return DbhResponse(-1, None)
            finally:
                self.disconnect()  # Disconnect after executing the function

        return wrapper

    @decorator_connection
    def get_all_users(self):
        with self._connection.cursor() as cur:
            cur.execute("SELECT username FROM Users")

            rows = cur.fetchall()
            return [row[0] for row in rows]

    @decorator_connection
    def get_user(self, username):
        with self._connection.cursor() as cur:
            cur.execute("SELECT username, password_data FROM Users WHERE username = %s", (username,))

            row = cur.fetchone()
            if row:
                return row
            else:
                return None

    @decorator_connection
    def add_user(self, username, password):
        with self._connection.cursor() as cur:
            cur.execute("INSERT INTO Users (username, password_data) VALUES (%s, %s)", (username, password))
            self._connection.commit()
            return True

    @decorator_connection
    def store_message(self, sender, receiver, message, timestamp):
        sql = """
                    INSERT INTO Messages (sender, receiver, text, timestamp)
                    VALUES (%s, %s, %s, %s)
                """

        with self._connection.cursor() as cur:
            cur.execute(sql, (sender, receiver, message, timestamp))
            self._connection.commit()
            return True

    @decorator_connection
    def get_chat_messages(self, sender, receiver):
        sql = """
                SELECT sender, receiver, text, timestamp
                FROM Messages
                WHERE (sender = %s AND receiver = %s)
                OR (sender = %s AND receiver = %s)
                ORDER BY timestamp
            """
        with self._connection.cursor() as cur:
            cur.execute(sql, (sender, receiver, receiver, sender))
            messages = []
            for row in cur.fetchall():
                message = {
                    'sender': row[0],
                    'receiver': row[1],
                    'text': row[2],
                    'timestamp': format_timestamp(row[3])
                }
                messages.append(message)
            return messages




