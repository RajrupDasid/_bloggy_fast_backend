import os
from pathlib import Path
from pydantic import BaseSettings, Field
from functools import lru_cache

os.environ['CQLENG_ALLOW_SCHEMA_MANAGEMENT'] = "1"

class Settings(BaseSettings):
    base_dir: Path = Path(__file__).resolve().parent
    keyspace: str = Field(..., env='ASTRADB_KEYSPACE')
    db_client_id: str = Field(..., env='ASTRADB_CLIENT_ID')
    db_client_secret: str = Field(..., env='ASTRADB_CLIENT_SECRET')
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field(..., env='ALGORITHM')
    session_duration: int = Field(default=86400)

    class Config:
        env_file = '.env'

@lru_cache
def get_settings():
    return Settings()
