# Load users from db
from passlib.context import CryptContext
import redis
import os


pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)


def get_user(username: str):
    r = redis.from_url(os.environ.get("REDIS_URL"))

    if r.hexists("user:" + username, "id") is False:
        return None

    userid = r.hget("user:" + username, "id")

    return {'id': int(userid)}


def check_password(username: str, password: str):
    r = redis.from_url(os.environ.get("REDIS_URL"))

    passHash = r.hget("user:" + username, "password").decode("utf-8")

    if pwd_context.verify(password, passHash):
        return True
    else:
        return False


# return True if succesfully added
def add_user(username: str, email: str, password: str, info: str):
    r = redis.from_url(os.environ.get("REDIS_URL"))

    # username already in use
    if r.hexists("user:" + username, "id"):
        return False

    ucount = r.incr("user_count")
    r.hset("user:" + username, key="id", value=ucount)
    r.hset("user:" + username, key="password", value=pwd_context.hash(password))
    r.hset("user:" + username, key="email", value=email)
    r.hset("user:" + username, key="info", value=info)

    return True
