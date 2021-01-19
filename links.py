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
        item['id'.encode("utf-8")] = x
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


def switch_state(link: int, user: int):
    r = redis.from_url(os.environ.get("REDIS_URL"))

    print("links.switch_state()")
    # check if user owns this link
    owned = r.lrange("owned:" + str(user), 0, -1)

    userLinks = []
    for x in owned:
        userLinks.append(int(x.decode("utf-8")))

    if link in userLinks:
        if r.hexists("links:" + str(link), "hidden"):
            if r.hget("links:" + str(link), "hidden") == "false":
                r.hset("links:" + str(link), "hidden", "true")
            else:
                # r.hset("links:" + str(link), "hidden", "false")
                r.hdel("links:" + str(link), "hidden")
        else:
            r.hset("links:" + str(link), "hidden", "true")
        return True
    else:
        return False
