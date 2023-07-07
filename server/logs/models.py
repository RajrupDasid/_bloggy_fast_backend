import logging
import uuid
from datetime import datetime
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from server.config import get_settings
from cassandra.cqlengine.columns import DateTime

settings = get_settings()

class Log(Model):
    __keyspace__ = settings.keyspace
    __table_name__ = 'applog'
    app_logging_id = columns.UUID(primary_key=True, default=uuid.uuid4)
    server_log_timestamp = DateTime(default=datetime.now)
    event = columns.Text()
    value = columns.Text()



class CustomLogger:
    @staticmethod
    def log_success(value):
        server_log_timestamp = datetime.now()
        log = Log(server_log_timestamp=server_log_timestamp, event="Success", value=value)
        log.save()

    @staticmethod
    def log_error(value):
        server_log_timestamp = datetime.now()
        log = Log(server_log_timestamp=server_log_timestamp, event="Error", value=value)
        log.save()
