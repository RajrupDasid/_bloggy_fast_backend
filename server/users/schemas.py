from pydantic import(
    BaseModel,
    EmailStr,
    SecretStr,
    validator,
    root_validator
)
from . import auth
from .models import User

class  UserLoginSchema(BaseModel):
    email: EmailStr
    password: SecretStr
   
    @root_validator 
    def validate_user(cls, values):
        err_msg = "Incorrect credentials enterd, please try again"
        email = values.get("email") or None
        print(email)
        password = values.get("password") or None
        print(password)

        if email is None or password is None:
            raise ValueError(err_msg)
    
        password = password.get_secret_value()
        user_obj =  auth.authenticate(email, password) 
        if  user_obj is None:
            raise ValueError("Invalid credentials:")
        token = auth.login(user_obj)
        print(token)
        return {"intercom":token}

class UserSignupSchema(BaseModel):
    email: EmailStr
    username: str
    password: str
    password_confirm: str
        
    
    @validator("email")
    def email_available(cls, v, values, **kwargs):
        q = User.objects.filter(email=v).allow_filtering()
        if q.count() != 0:
            raise ValueError("An user with the same email address already exists")
        return v
        
    @validator("password_confirm")
    def passwords_match(cls, v, values, **kwargs):
        password = values.get('password')
        password_confirm = v
        if password != password_confirm:
            raise ValueError("Passwords do not match")
        return v
