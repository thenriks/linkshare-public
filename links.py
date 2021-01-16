# Link loading and adding
import redis
import os

# load links of user specified
def load_links(user: int):
    r = redis.from_url(os.environ.get("REDIS_URL"))
    
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
    r = redis.from_url(os.environ.get("REDIS_URL"))

    nid = r.incr("link_count")
    r.hset("links:" + str(nid), key="url", value=url)
    r.hset("links:" + str(nid), key="info", value=info)

    r.lpush("owned:" + str(uid), nid)
