from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setting import config
from contextlib import contextmanager

settings = config.get_settings()

SQL_ALCHEMY_URL = (
    f"mssql+pyodbc://{settings.pg_user}:{settings.pg_password}"
    f"@{settings.pg_host}:{settings.pg_port}/{settings.pg_database}"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&encrypt=yes"
    "&trustServerCertificate=no"
    "&hostNameInCertificate=*.database.windows.net"
)

ENGINE = create_engine(SQL_ALCHEMY_URL, echo=settings.debug, pool_size=20, max_overflow=10)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE, expire_on_commit=False)

@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()