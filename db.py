from sqlalchemy import create_engine, text


def create_request(sql_request):
    engine = create_engine(
        "postgresql://postgres_user:rkKMi4^6e7WK&J@158.160.90.47:5432/pokemon_stable"
    )

    with engine.connect() as connection:
        result = connection.execute(text(sql_request))
        data = [row._asdict() for row in result]
    return data


