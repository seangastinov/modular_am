from setting import config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

settings = config.get_settings()

SQL_ALCHEMY_URL = f"postgresql+psycopg://{settings.pg_user}:{settings.pg_password}@{settings.pg_host}:{settings.pg_port}/{settings.pg_database}"

SQL_ALCHEMY_URL = (
    f"mssql+aioodbc://{settings.pg_user}:{settings.pg_password}"
    f"@{settings.pg_host}:{settings.pg_port}/{settings.pg_database}"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&encrypt=yes"
    "&trustServerCertificate=no"
    "&hostNameInCertificate=*.database.windows.net"
)

ENGINE = create_async_engine(SQL_ALCHEMY_URL, echo=settings.debug, pool_size=20, max_overflow=10)

AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=ENGINE, class_=AsyncSession
)


from typing import AsyncGenerator


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = AsyncSessionLocal()
    try:
        yield async_session
        await async_session.commit()
    except Exception as e:
        await async_session.rollback()
        raise e
    finally:
        await async_session.close()
