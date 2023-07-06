import datetime
from jose import jwt,JWTError, ExpiredSignatureError
from typing import Annotated
from server import config
from .models import User

settings = config.get_settings()

def authenticate(email,password):
    try:
        user_obj =  User.objects.get(email=email)
    except Exception as e:
        user_obj = None
    if not user_obj.verify_password(password):
        return None
    return user_obj

def login(user_obj,expires=settings.session_duration):
    raw_data = {
        "uid":f"{user_obj.uid}",
        "role":"mainuser",
        "exp": datetme.datetime.utcnow() + datetime.timedelta(seconds=expires)
    }
    return jwt.encode(raw_data, settings.secret_key, algorithm=settings.jwt_algorithm)

def verify_user_id(token):
    data = {}
    try:
        data = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    
    except ExpiredSignatureError as e:
        print (e)
    except:
        pass
    if 'uid' not in data:
        return None
    return data
