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
    "http://127.0.0.1:8000/*",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8000/login",
    "http://127.0.0.1:8000/links",
    "http://127.0.0.1:8000/links/2",
    "http://127.0.0.1:9000/prot",
    "http://127.0.0.1:9000/login",
    "http://127.0.0.1:9000",
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
    # user = fake_db.get(email)
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

    return {'access_token': access_token, 'token_type': 'bearer', 'user_id': user['id']}


@app.get("/")
async def main():
    return RedirectResponse(url='/-')


# Get links owned by specified user
@app.get("/links/{user_id}")
async def get_links(user_id):
    user_links = None

    user_links = links.load_links(user_id)

    return user_links


# Add link
@app.post("/add_link/")
async def add_link(link: Link, user=Depends(manager)):
    # Voisi palauttaa nykyisen linkkilistan?

    if link.uid == user.get("id"):
        links.add_link(link.url, link.info, user.get("id"))


@app.post("/add_user/")
async def add_user(newUser: User):
    users.add_user(newUser.username, newUser.email, newUser.password, newUser.info)

    return "OK!"


@app.get("/error")
async def login_error():
    return "Not logged in!"

