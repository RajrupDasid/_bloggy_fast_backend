import uuid
from server.config import get_settings
from server.users.exceptions import InvalidUserIDException
from server.users.models import User
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.query import (DoesNotExist, MultipleObjectsReturned)
from datetime import datetime
from cassandra.cqlengine.columns import DateTime

settings = get_settings()

class DateTimeWithUpdate(columns.DateTime):
    def pre_save(self, model_instance, column):
        value = super().pre_save(model_instance, column)
        setattr(model_instance, column.db_field, value)
        return value

class Video(Model):
    __keyspace__ = settings.keyspace
    __table_name__ = 'video'
    vid = columns.UUID(primary_key=True, default=uuid.uuid4)
    user_id = columns.UUID()
    title = columns.Text()
    description = columns.Text()
    file_name = columns.Text()
    create_time = DateTime(default=datetime.now)
    update_time = DateTimeWithUpdate(default=datetime.now)

    @staticmethod
    def add_video(user_id, title, description, file_name):
        video = Video.create(
            user_id = user_id,
            title = title,
            description = description,
            file_name = file_name
        )
        return video

    
