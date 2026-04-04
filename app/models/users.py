from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String, default="buyer")  # buyer/seller

    products: Mapped[list["Product"]] = relationship("Product", back_populates='seller')
    cart_items: Mapped[list['CartItem']] = relationship('CartItem', back_populates='user', cascade='all, delete-orphan')
    orders: Mapped[list['Order']] = relationship('Order', back_populates='user', cascade="all, delete-orphan")

