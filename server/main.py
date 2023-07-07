import json
import pathlib
from typing import Optional,List
from fastapi import FastAPI, Request, Form, status, HTTPException

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



app = FastAPI()


DB_SESSION = None
BASE_DIR = pathlib.Path(__file__).resolve().parent # app/
#app.add_middleware(AuthenticationMiddleware, backend=JWTCookieBackend())


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
async def create_user(request: UserLoginSchema):
    try:
        email = request.email
        password = request.password
        user = User.create_user(email, password)
        success_message = f"User created successfully - Email -  {email}"
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
            raise HTTPException(status_code=400, detail="Incorrect credentials entered, please try again")

        user_obj = auth.authenticate(email, password)
        if user_obj is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = auth.login(user_obj)

        return {"intercom": token}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An error occurred while processing the login")













    #try:
     #   email = request.email
     #   password = request.password
    #    raw_data = {

     #       "email": email,
      #      "password": password,
     #   }
      #  user_login = UserLoginSchema(**raw_data)
     #   user_login.validate_user()
       # data, errors = utils.valid_schema_data_or_error(raw_data,UserLoginSchema)
        #context = {
        #    "data" : data,
        #    "error": errors
        #}
        
       # return JSONResponse(content={"ojj":"nlcnlzxnclzxnclzxnclz"})
   # except Exception as e:
    #    print (e)
    #    return JSONResponse(content={"error":" please rectify the logic"})



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
