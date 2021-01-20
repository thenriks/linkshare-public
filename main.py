from typing import Optional
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
import links
import users


class NotAuthenticatedException(Exception):
    pass


app = FastAPI()
app.mount("/-", StaticFiles(directory="static", html=True), name="static")

origins = [
    "http://localhost",
    "http://localhost:8080",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Link(BaseModel):
    url: str
    info: str
    uid: int


class LinkState(BaseModel):
    linkId: int


class User(BaseModel):
    username: str
    password: str
    email: str
    info: str


SECRET = "SuuriSalaisuus"
manager = LoginManager(SECRET, tokenUrl='/auth/token')


def exc_handler(request, exc):
    return RedirectResponse(url='/error')
    # return "Login failed!"


manager.not_authenticated_exception = NotAuthenticatedException
app.add_exception_handler(NotAuthenticatedException, exc_handler)


@manager.user_loader
def load_user(username: str):
    user = users.get_user(username)
    return user


@app.post('/auth/token')
def login(data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password

    user = load_user(username)
    if not user:
        raise InvalidCredentialsException
    elif users.check_password(username, password) is False:
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
        data=dict(sub=username), expires_delta=timedelta(hours=1)
    )

    return {'access_token': access_token, 'token_type': 'bearer', 'user_id': user['id'], 'info': user['info']}


@app.get("/")
async def main():
    return RedirectResponse(url='/-')


# Get links owned by specified user
# TODO: Separate link loading for owner and others so no hidden links are sen to others
@app.get("/links/{user_id}")
async def get_links(user_id):
    user_links = None

    user_links = links.load_links(user_id)

    return user_links


# Add link
@app.post("/add_link/")
async def add_link(link: Link, user=Depends(manager)):
    if len(link.url) > 2000 or len(link.info) > 100:
        return "Error adding link!"

    if link.uid == user.get("id"):
        links.add_link(link.url, link.info, user.get("id"))

    return "Link added!"


# Switch Link visibility
@app.post("/switch_state/")
async def switch_state(state: LinkState, user=Depends(manager)):
    links.switch_state(state.linkId, user.get("id"))
    print("switch_state")
    return "OK"


@app.post("/add_user/")
async def add_user(newUser: User):
    result = users.add_user(newUser.username, newUser.email, newUser.password, newUser.info)

    if result:
        return "Account created."
    else:
        return "Could not create account."


@app.get("/user_info/{user_id}")
async def user_info(user_id: int):
    return users.user_info(user_id)


@app.get("/new_users/")
async def new_users():
    return users.get_newest()


@app.get("/error")
async def login_error():
    return "Not logged in!"
