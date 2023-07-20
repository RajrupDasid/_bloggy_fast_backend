import json
import pathlib
from typing import Optional,List
from fastapi import FastAPI, Request, Form, status, HTTPException,WebSocket, Response, Cookie, Depends
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
from .users import auth
from fastapi.responses import JSONResponse,PlainTextResponse
from pydantic import BaseModel, SecretStr, EmailStr
from .video.models import Video
from fastapi.exceptions import RequestValidationError
from .logs.models import Log, CustomLogger
from cassandra.cqlengine.query import BatchQuery
from cassandra.query import SimpleStatement
from fastapi.encoders import jsonable_encoder
from .ses.security import sessionid, csrfid, generate_key, encrypt_token, decrypt_token
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


DB_SESSION = None
BASE_DIR = pathlib.Path(__file__).resolve().parent # app/
#app.add_middleware(AuthenticationMiddleware, backend=JWTCookieBackend())
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set this to restrict origins, e.g., ["http://localhost", "https://example.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Set this to restrict HTTP methods, e.g., ["GET", "POST"]
    allow_headers=["*"],  # Set this to restrict headers, e.g., ["X-Requested-With", "Content-Type"]
)


@app.on_event("startup")
def on_startup():
    # triggered when fastapi starts
    print("syncing tables ")
    global DB_SESSION
    DB_SESSION = db.get_session()
    try:
        sync_table(User)
        print("user table sync complete")
    except Exception as e:
        print (e)
    try:
        sync_table(Video)
        print("video table sync complete")
    except Exception as e:
        print (e)
    try:
        sync_table(Log)
        print("app server log table sync complete")
    except Exception as e:
        print(e)

class UserRegistrationResponse(BaseModel):
    email: EmailStr
    password: SecretStr

@app.post('/users/signup', response_model=UserRegistrationResponse)
async def create_user(request: UserSignupSchema):
    try:
        email = request.email
        username = request.username
        password = request.password

        user = User.create_user(email,username, password)
        success_message = f"User with {username} - {email} has been  created successfully"
        CustomLogger.log_success(success_message)
        return JSONResponse(content={"Success":"User singned_up successfully"}, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        CustomLogger.log_error(error_message)
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginResponse(BaseModel):
    email: EmailStr
    password: SecretStr


@app.post("/users/login")
async def login_user(request: LoginResponse):
    try:
        email = request.email
        password = request.password.get_secret_value()

        if not email or not password:
            error_message = "User made a blank request"
            CustomLogger.log_error(error_message)
            return JSONResponse(content={"error":"Details cannot be blanked"}, status_code = status.HTTP_400_BAD_REQUEST)

        user_obj = auth.authenticate(email, password)
        if user_obj is None:
            error_message = f"User with email - {email} is either not exists or gave wrong credential"
            CustomLogger.log_error(error_message)
            return JSONResponse(content={"error":"User credential not matched"}, status_code = status.HTTP_404_NOT_FOUND)

        token = auth.login(user_obj)
        key = generate_key()
        etoken = encrypt_token(token,key)

        response = {"intercom":etoken, "_intercom_csrf_token": csrfid() , "_intercom_session_id":sessionid()}
        success_message = f"User successfully logged in - the user details is -logged in user email-{email} - logged in user token {token} - logged in user response {response}"
        CustomLogger.log_success(success_message)
        return response
        
    except Exception as e:
        error_message = f"Something went wrong and the error debugging is - {str(e)}"
        CustomLogger.log_error(error_message)

        return JSONResponse(content={"error":"Server error occured"}, status_code = status.HTTP_500_INTERNAL_SERVER_ERROR)


class IndexPage(BaseModel):
    response : str

# @app.get("/")
# async def index():
 #   response = "Hello world"
  #  return response
        



class LogResponse(BaseModel):
    app_logging_id: str
    server_log_timestamp: str
    event: str
    value: str

@app.get('/logs', response_model=List[LogResponse])
async def get_logs():
    logs = Log.objects.all()
    response = []
    for log in logs:
        log_response = LogResponse(
            app_logging_id = str(log.app_logging_id),
            server_log_timestamp=str(log.server_log_timestamp),
            event=log.event,
            value=log.value
        )
        response.append(log_response)
    return JSONResponse(content=jsonable_encoder(response))


# class AllUser(BaseModel):
  #  email: str
   #  password: str

# @app.get('/users', response_model=List[AllUser])
# async def get_users():
  #  all_users = User.objects.all()
   # response = [AllUser(email=user.email, password=user.password) for user in all_users]
   # response_dicts = [user.dict() for user in response]
   # return JSONResponse(content=response_dicts)
