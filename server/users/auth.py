import datetime
from jose import jwt,JWTError, ExpiredSignatureError
from typing import Annotated
from server import config
from .models import User
from .security import verify_hash

settings = config.get_settings()

def authenticate(email, password):
    # step 1
    try:
        #q = User.objects.filter(email=)
        q = User.objects.filter(email=email).allow_filtering()
        user_obj = q.get()
        

    except Exception as e:
        print(e)
        user_obj = None
    if user_obj:
        if not user_obj.verify_password(password):
            return None
    return user_obj



def login(user_obj,expires=settings.session_duration):
    raw_data = {
        "uid":f"{user_obj.uid}",
        "role":"mainuser",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=expires)
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
