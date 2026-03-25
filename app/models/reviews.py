from sqlalchemy import Text, Integer, Boolean, DateTime, ForeignKey, CheckConstraint
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Reviews(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    grade: Mapped[int] = mapped_column(Integer, CheckConstraint('grade >= 1 And grade <= 5'), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)