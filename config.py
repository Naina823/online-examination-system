import os


class Config:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-this-later"
    )

    database_url = os.environ.get(
        "DATABASE_URL",
        "sqlite:///database.db"
    )

    # Render/Postgres may provide a postgres:// URL.
    # SQLAlchemy expects postgresql:// or postgresql+psycopg://.
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1
        )

    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    SQLALCHEMY_DATABASE_URI = database_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False