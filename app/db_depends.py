from sqlalchemy.orm import Session
from collections.abc import Generator, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal, async_session_maker


def get_db() -> Generator[Session, None, None]:
    '''
    Зависимость для получения сессии БД. Создаёт новую сессию для каждого запроса и закрывает её после обработки
    '''
    db: Session = SessionLocal()
    try:
        yield db
    except:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет асинхронную сессию SQLAlchemy для работы с базой данных PostgreSQL.
    """
    async with async_session_maker() as session:
        yield session
