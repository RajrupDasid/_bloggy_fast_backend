import json
import pathlib
from typing import Optional
from fastapi import FastAPI, Request, Form
from .config import get_settings
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import requires
from cassandra.cqlengine.management import sync_table
from pydantic.error_wrappers import ValidationError
from . import config, db, utils
from .users.backends import JWTCookieBackend
from .users.decorators import login_required
from .users.models import User
from .users.schemas import (
    UserLoginSchema,
    UserSignupSchema
)
from fastapi.responses import JSONResponse,PlainTextResponse
from pydantic import BaseModel, SecretStr, EmailStr

app = FastAPI()

DB_SESSION = None
BASE_DIR = pathlib.Path(__file__).resolve().parent # app/
#app.add_middleware(AuthenticationMiddleware, backend=JWTCookieBackend())

@app.on_event("startup")
def on_startup():
    # triggered when fastapi starts
    print("hello world")
    global DB_SESSION
    DB_SESSION = db.get_session()
    sync_table(User)

class UserRegistrationResponse(BaseModel):
    email: EmailStr
    password: SecretStr
    password_confirm: SecretStr

@app.post('/signup',response_model=UserRegistrationResponse)
async def create_user(request: UserSignupSchema):
    email = request.email
    print(email)
    password = request.password
    print(password)
    user = await User.create_user(email, password)

    response = UserRegistrationResponse(email=email, password=password)
    return response
