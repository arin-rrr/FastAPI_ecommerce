from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from datetime import datetime

DATABASE_URL = 'sqlite:///ecommerce.db'
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    sku = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    description = Column(String(500), default="")
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

