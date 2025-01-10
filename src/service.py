from typing import Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from jinjasql import JinjaSql


def get_total_flights(
    db: Session,
    params: dict,
) -> int:
    # Simulate processing of POST data
    j = JinjaSql(param_style="named")

    query_template = """
    SELECT COUNT(*)
    FROM flights
    WHERE 
    {% if typology == 'departure' %}
    departure_date >= {{ start_date }} AND departure_date <= {{ end_date }}
    {% endif %}
    {% if typology == 'arrival' %}
    arrival_date >= {{ start_date }} AND arrival_date <= {{ end_date }}
    {% endif %}
    {% if airport_codes and typology == 'departure'  %}
    AND departure_airport_code IN {{ airport_codes | inclause }}
    {% endif %}
    {% if airport_codes and typology == 'arrival'  %}
    AND arrival_airport_code IN {{ airport_codes | inclause }}
    {% endif %}
    """

    query, bind_params = j.prepare_query(query_template, params)
    query = text(query).bindparams(**bind_params)

    resultproxy = db.execute(query)
    result = resultproxy.fetchone()
    result_dict = dict(zip(resultproxy.keys(), result))

    return {
        "result": "processed",
        "data": result_dict,
    }
