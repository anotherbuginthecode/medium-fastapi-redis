from redis import Redis
from typing import Optional, Union
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = (
    "postgresql://postgres:postgres@db:5432/postgres"  # keep in .env when in prod
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RedisWrapper:
    def __init__(self) -> None:
        self.client = Redis(host="redis", port=6379)

    def create_cache_key(self, request_data: dict) -> str:
        # convert list type to fullstring to make it hashable
        for key, value in request_data.items():
            if isinstance(value, list):
                request_data[key] = " ".join(value)

        return f"post_cache:{hash(frozenset(request_data.items()))}"

    def convert_payload_to_query_params(
        self, endpoint: str, payload: Optional[Union[dict, None]] = None
    ) -> str:
        query_params_list = []
        if not payload:
            return f"{endpoint}"

        for i, (key, val) in enumerate(payload.items()):
            if val:
                query_params_list.append(f"{key}={val}")
        return f"{endpoint}?{'&'.join(query_params_list)}"

    def store_in_cache(self, key: str, value: str, expire_time: int = 60):
        return self.client.setex(key, expire_time, value)

    def get_from_cache(self, key: str):
        return self.client.get(key)
