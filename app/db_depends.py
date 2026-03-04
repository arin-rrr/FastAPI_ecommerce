from sqlalchemy.orm import Session
from collections.abc import Generator

from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    '''
    Зависимость для получения сессии БД. Создаёт новую сессию для каждого запроса и закрывает её после обработки
    '''
    db: Session = SessionLocal()
    try:
        yield db
    except:
        db.close()
