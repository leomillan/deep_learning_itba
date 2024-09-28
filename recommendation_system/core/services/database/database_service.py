import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

Base = declarative_base()


class DatabaseService:

    def __init__(self, config, drop_tables: bool = False):

        user = config.get("user")
        password = os.environ[config.get("pass")]
        url = config.get("url")
        port = config.get("port")
        database = config.get("database")

        self.engine = create_engine(
            f"postgresql+psycopg2://{user}:{password}@{url}:{port}/{database}"
        )
        self.db_session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )

        Base.query = self.db_session.query_property()
        self.init_db(engine=self.engine, drop_tables=drop_tables)

    @staticmethod
    def init_db(engine, drop_tables):
        # import all modules here that might define models so that
        # they will be registered properly on the metadata.  Otherwise
        # you will have to import them first before calling init_db()
        from core.services.database import Movie, Rating, User  # noqa

        if drop_tables:
            Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
