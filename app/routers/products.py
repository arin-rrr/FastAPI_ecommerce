from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db_depends import get_db
from app.schema import Product as ProductSchema, ProductCreate
from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel

router = APIRouter(
    prefix='/products',
    tags=['products']
)


@router.get('/')
async def get_all_products():
    '''
    To get the list of all products
    '''
    return {'message': 'Список всех продуктов.'}


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ProductSchema)  # определяем код ответа и модель ответа
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):  # модель для создания и БД
    '''
    To create a new product
    '''
    # проверяем, что такая категория существует
    stmt_category_id = select(CategoryModel.id).where(CategoryModel.is_active==True, CategoryModel.id == product.category_id)
    res_category_id = db.scalars(stmt_category_id).all()
    if res_category_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category not found or inactive')
    new_product = ProductModel(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

    return {'message': 'Товар создан.'}


@router.get('/category/{category_id}')
async def get_product_by_category(category_id: int):
    '''
    To get all products in category by category_id
    '''
    return {'message': f'Товары в категории {category_id}'}


@router.get('/{product_id}')
async def get_product_info_by_id(product_id: int):
    '''
    To get a product info by product_id
    '''
    return {'message': f'Детали товара с ID = {product_id}'}


@router.put('/{product_id}')
async def update_product(product_id: int):
    '''
    To update product info by product_id
    '''
    return {'message': f'Товар с ID {product_id} обновлен'}


@router.delete('/{product_id}')
async def delete_product(product_id: int):
    '''
    To delete a product by product_id
    '''
    return {'message': f'Товар с ID {product_id} удален'}
