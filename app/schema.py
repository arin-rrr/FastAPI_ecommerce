from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


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
