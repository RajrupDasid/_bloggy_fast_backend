import uuid
from server.config import get_settings
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from . import exceptions, security, validators
from datetime import datetime
from cassandra.cqlengine.columns import DateTime

settings = get_settings()

class DateTimeWithUpdate(columns.DateTime):
    def pre_save(self, model_instance, column):
        value = super().pre_save(model_instance, column)
        setattr(model_instance, column.db_field, value)
        return value


class User(Model):
    __keyspace__ = settings.keyspace
    __table_name__ = 'user'
    uid = columns.UUID(primary_key=True, default=uuid.uuid4)
    username = columns.Text()
    email = columns.Text(primary_key=True)
    password = columns.Text()
    create_time = DateTime(default=datetime.now)
    update_time = DateTimeWithUpdate(default=datetime.now)


    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"User(email={self.email}, user_id={self.uid})"

    def set_password(self, pw, commit=False):
        pw_hash = security.generate_hash(pw)
        self.password = pw_hash
        if commit:
            self.save()
        return True

    def verify_password(self,pw_str):
        pw_hash = self.password
        verified, _ = security.verify_hash(pw_hash, pw_str)
        return verified

    @staticmethod
    def create_user(email,username, password=None):
        q = User.objects.filter(email=email).allow_filtering()
        if q.count() != 0:
            raise exceptions.UserHasAccountException("An user with same email already exists")
        v = User.objects.filter(username=username).allow_filtering()
        if v.count() !=0 :
            raise exceptions.UsernameException("An user with this user name already exists")
        valid, msg, email = validators._validate_email(email)
        if not valid:
            raise exceptions.InvalidEmailException(f"Invalid email:{msg}")
        obj = User(email=email, username=username)
        obj.set_password(password)
        obj.save()
        return obj

    @staticmethod
    def check_exists(username,email):
        q = User.objects.filter(username=username).allow_filtering()
        p = User.objects.filter(email=email).allow_filtering()

        return  q.count() != 0 or p.count() !=0
    
    @staticmethod
    def check_user_by_uid(uid):
        v = User.objects.filter(uid=uid).allow_filtering()
        return v.count() !=0

    @staticmethod
    def by_user_id(uid=None):
        q = User.objects.filter(uid=uid).allow_filtering()
        if q.count() != 1:
            return None
        return q.first()

