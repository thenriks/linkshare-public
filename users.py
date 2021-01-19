# Load users from db
from passlib.context import CryptContext
import redis
import os


pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)


def get_user(username: str):
    r = redis.from_url(os.environ.get("REDIS_URL") + "?ssl_cert_reqs=none")

    if r.hexists("user:" + username, "id") is False:
        return None

    userid = r.hget("user:" + username, "id")
    userinfo = r.hget("user:" + username, "info")

    return {'id': int(userid), 'info': userinfo}


def check_password(username: str, password: str):
    r = redis.from_url(os.environ.get("REDIS_URL") + "?ssl_cert_reqs=none")

    passHash = r.hget("user:" + username, "password").decode("utf-8")

    if pwd_context.verify(password, passHash):
        return True
    else:
        return False


# return True if succesfully added
def add_user(username: str, email: str, password: str, info: str):
    r = redis.from_url(os.environ.get("REDIS_URL") + "?ssl_cert_reqs=none")

    # username already in use
    if r.hexists("user:" + username, "id"):
        return False

    if len(username) > 32 or len(email) > 64 or len(password) > 64 or len(info) > 300:
        return False

    ucount = r.incr("user_count")

    # userid:id connects id to username
    r.set("userid:" + str(ucount), username)

    r.hset("user:" + username, key="id", value=ucount)
    r.hset("user:" + username, key="password", value=pwd_context.hash(password))
    r.hset("user:" + username, key="email", value=email)
    r.hset("user:" + username, key="info", value=info)

    # List of newest users
    r.lpush("newest", ucount)
    if r.llen("newest") > 5:
        r.rpop("newest")

    return True


def user_info(uid: int):
    r = redis.from_url(os.environ.get("REDIS_URL") + "?ssl_cert_reqs=none")

    username = r.get("userid:" + str(uid))

    if r.hexists("user:" + username.decode("utf-8"), "info"):
        return r.hget("user:" + username.decode("utf-8"), "info")
    else:
        return "UNDEFINED"


def get_newest():
    r = redis.from_url(os.environ.get("REDIS_URL") + "?ssl_cert_reqs=none")

    new_users = r.lrange("newest", 0, -1)

    userlist = []

    for x in new_users:
        i = {}
        i['id'] = "#/v/" + x.decode("utf-8")
        name = r.get("userid:" + x.decode("utf-8")).decode("utf-8")
        i['username'] = name
        userlist.append(i)

    return userlist
