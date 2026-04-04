from pydantic import BaseModel, Field, ConfigDict, EmailStr
from decimal import Decimal
from datetime import datetime


class CategoryCreate(BaseModel):
    '''
    Data category Model for PUT and POST methods
    '''
    name: str = Field(..., min_length=3, max_length=50, description='Название категории (3-50 символов)')
    parent_id: int | None = Field(None, description='ID родительской категории, если есть')


class Category(BaseModel):
    '''
    Data category Model for API responses
    '''
    id: int = Field(..., description='Уникальный ID категории')
    name: str = Field(..., description='Название категории')
    parent_id: int | None = Field(None, description='ID родительской категории, если есть')
    is_active: bool = Field(..., description='Активность категории')
    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    '''
    Data product Model for PUT and POST methods
    '''
    name: str = Field(..., min_length=3, max_length=100, description='Название товара (3-100 символов)')
    description: str | None = Field(None, max_length=500, description="Описание товара (до 500 символов)")
    price: Decimal = Field(..., gt=0, decimal_places=2, description='Цена товара (больше 0)')
    image_url: str | None = Field(None, max_length=200, description="URL изображения товара")
    stock: int = Field(..., ge=0, description='Количество товаров на складе (0 и более)')
    category_id: int = Field(..., description='ID категории товара')


class Product(BaseModel):
    """
    Data product Model for API responses
    """
    id: int = Field(..., description="Уникальный идентификатор товара")
    name: str = Field(..., description="Название товара")
    description: str | None = Field(None, description="Описание товара")
    price: Decimal = Field(..., description="Цена товара в рублях", gt=0, decimal_places=2)
    image_url: str | None = Field(None, description="URL изображения товара")
    stock: int = Field(..., description="Количество товара на складе")
    category_id: int = Field(..., description="ID категории")
    is_active: bool = Field(..., description="Активность товара")
    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    role: str
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr = Field(description='Email пользователя')
    password: str = Field(min_length=8, description='Пароль (минимум 8 символов)')
    role: str = Field(default="buyer", pattern="^(buyer|seller)$", description="Роль: 'buyer' или 'seller'")


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ReviewCreate(BaseModel):
    product_id: int = Field(..., description='ID товара')
    comment: str | None = Field(None, description='Отзыв')
    grade: int = Field(..., ge=1, le=5)


class ReviewResponse(BaseModel):
    id: int
    user_id: int | None
    product_id: int | None
    comment: str | None
    comment_date: datetime
    grade: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    '''
    Список пагинации для товаров.
    '''
    items: list[Product] = Field(description='Товары для текущей страницы')
    total: int = Field(ge=0, description='Общее количество товаров')
    page: int = Field(ge=1, description='Номер текущей страницы')
    page_size: int = Field(ge=1, description='Количество элементов на странице')
    model_config = ConfigDict(from_attributes=True)


class CartItemBase(BaseModel):
    product_id: int = Field(description='ID товара')
    quantity: int = Field(description='Количество товара', ge=1)


class CartItemCreate(CartItemBase):  # for POST
    pass


class CartItemUpdate(BaseModel):
    '''
    Модель обновления количества товара в корзине
    '''
    quantity: int = Field(..., ge=1, description='Новое количечтво товара')


class CartItem(BaseModel):
    id: int = Field(..., description="ID позиции корзины")
    quantity: int = Field(..., ge=1, description="Количество товара")
    product: Product = Field(..., description='Информация о товаре')

    model_config = ConfigDict(from_attributes=True)


class Cart(BaseModel):
    """Полная информация о корзине пользователя."""
    user_id: int = Field(..., description="ID пользователя")
    items: list[CartItem] = Field(default_factory=list, description="Содержимое корзины")
    total_quantity: int = Field(..., ge=0, description="Общее количество товаров")
    total_price: Decimal = Field(..., ge=0, description="Общая стоимость товаров")

    model_config = ConfigDict(from_attributes=True)


class OrderItem(BaseModel):
    id: int = Field(..., description="ID позиции заказа")
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(..., ge=1, description="Количество")
    unit_price: Decimal = Field(..., ge=0, description="Цена за единицу на момент покупки")
    total_price: Decimal = Field(..., ge=0, description="Сумма по позиции")
    product: Product | None = Field(None, description="Полная информация о товаре")

    model_config = ConfigDict(from_attributes=True)

class Order(BaseModel):
    id: int = Field(..., description="ID заказа")
    user_id: int = Field(..., description="ID пользователя")
    status: str = Field(..., description="Текущий статус заказа")
    total_amount: Decimal = Field(..., ge=0, description="Общая стоимость")
    created_at: datetime = Field(..., description="Когда заказ был создан")
    updated_at: datetime = Field(..., description="Когда последний раз обновлялся")
    items: list[OrderItem] = Field(default_factory=list, description="Список позиций")

    model_config = ConfigDict(from_attributes=True)

class OrderList(BaseModel):
    items: list[Order] = Field(..., description="Заказы на текущей странице")
    total: int = Field(ge=0, description="Общее количество заказов")
    page: int = Field(ge=1, description="Текущая страница")
    page_size: int = Field(ge=1, description="Размер страницы")

    model_config = ConfigDict(from_attributes=True)