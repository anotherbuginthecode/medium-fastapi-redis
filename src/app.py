from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel
import json
from .service import get_total_flights
from .database import RedisWrapper, get_db
from enum import Enum

app = FastAPI()
redis_wrapper = RedisWrapper()


class FlightTypology(str, Enum):
    departure = "departure"
    arrival = "arrival"


class BaseRequestSchema(BaseModel):
    start_date: str
    end_date: str
    airport_codes: list[str] | None = None
    typology: FlightTypology = FlightTypology.departure

    class Config:
        use_enum_values = True


@app.post("/data")
async def handle_post(data: BaseRequestSchema, db=Depends(get_db)):
    cache_key = redis_wrapper.create_cache_key(data.model_dump())
    not_hashed_cache_key = redis_wrapper.convert_payload_to_query_params(
        endpoint="/data", payload=data.model_dump()
    )

    print("Not hashed cache key: ", not_hashed_cache_key)

    cached_response = redis_wrapper.get_from_cache(cache_key)
    if cached_response:
        return json.loads(cached_response)

    response_data = get_total_flights(
        db=db,
        params=data.model_dump(),
    )
    redis_wrapper.store_in_cache(cache_key, json.dumps(response_data))

    return response_data
