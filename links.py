# Link loading and adding
import redis
import os
try:
    import creds
except ImportError:
    pass

# load links of user specified
def load_links(user: int):
    if creds.REDISPATH is not None:
        r = redis.Redis(host=creds.REDISPATH, port=creds.REDISPORT, password=creds.REDISPASS)
    else:
        r = redis.from_url(os.environ.get("REDIS_TLS_URL"))
    links = []

    owned = r.lrange("owned:" + str(user), 0, -1)

    links = []

    for x in owned:
        print("links:" + x.decode("utf-8"))
        item = r.hgetall("links:" + x.decode("utf-8"))
        print(item)
        links.append(item)

    formatted = []

    for y in links:
        formatted.append({key.decode("utf-8"): val.decode("utf-8") for key, val in y.items()})

    return formatted


def add_link(url: str, info: str, uid: int):
    if creds.REDISPATH is not None:
        r = redis.Redis(host=creds.REDISPATH, port=creds.REDISPORT, password=creds.REDISPASS)
    else:
        r = redis.from_url(os.environ.get("REDIS_TLS_URL"))

    nid = r.incr("link_count")
    r.hset("links:" + str(nid), key="url", value=url)
    r.hset("links:" + str(nid), key="info", value=info)

    r.lpush("owned:" + str(uid), nid)
