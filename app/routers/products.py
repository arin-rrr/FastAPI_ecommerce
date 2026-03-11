from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_depends import get_db, get_async_db
from app.schema import Product as ProductSchema, ProductCreate
from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel

router = APIRouter(
    prefix='/products',
    tags=['products']
)


@router.get('/')
async def get_all_products(db: AsyncSession = Depends(get_async_db), status_code=status.HTTP_200_OK) -> list[
    ProductSchema]:
    '''
    To get the list of all products
    '''
    stmt = select(ProductModel).where(ProductModel.is_active == True)
    db_result = await db.scalars(stmt)
    active_products = db_result.all()
    return active_products


@router.post('/', status_code=status.HTTP_201_CREATED,
             response_model=ProductSchema)  # определяем код ответа и модель ответа
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_async_db)):  # модель для создания и БД
    '''
    To create a new product
    '''
    # проверяем, что такая категория существует
    stmt_category_id = select(CategoryModel.id).where(CategoryModel.is_active == True,
                                                      CategoryModel.id == product.category_id)
    category_id = await db.scalars(stmt_category_id)
    res_category_id = category_id.all()
    if res_category_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category not found or inactive')
    new_product = ProductModel(**product.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


@router.get('/category/{category_id}', status_code=status.HTTP_200_OK, response_model=list[ProductSchema])
async def get_product_by_category(category_id: int, db: AsyncSession = Depends(get_db)) -> list[ProductSchema]:
    '''
    To get all products in category by category_id
    '''
    active_category = select(CategoryModel).where(CategoryModel.is_active == True, CategoryModel.id == category_id)
    db_result = await db.scalars(active_category)
    res_active_category = db_result.first()
    if res_active_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found or inactive')
    products_by_category_id = select(ProductModel).where(ProductModel.category_id == category_id,
                                                         ProductModel.is_active == True)
    db_result = await db.scalars(products_by_category_id)
    result = db_result.all()
    if result is None:
        return []
    return result


@router.get('/{product_id}', response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product_info_by_id(product_id: int, db: AsyncSession = Depends(get_db)) -> ProductSchema:
    '''
    To get a product info by product_id
    '''
    active_product = select(ProductModel).where(ProductModel.is_active == True, ProductModel.id == product_id)
    db_active_product = await db.scalars(active_product)
    res_active_product = db_active_product.first()
    if res_active_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found or inactive')
    # проверем, что категория активна
    active_categories = select(CategoryModel.id).where(CategoryModel.is_active == True)
    db_active_categories = await db.scalars(active_categories)
    res_active_categories = db_active_categories.all()

    product_by_id = select(ProductModel.category_id).where(ProductModel.is_active == True, ProductModel.id == product_id)
    db_product_by_id = await db.scalars(product_by_id)
    if db_product_by_id.first() not in res_active_categories:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category not found or inactive')
    return db_product_by_id.first()


@router.put('/{product_id}')
async def update_product(product_id: int, new_product: ProductCreate, db: AsyncSession = Depends(get_db)):
    '''
    To update product info by product_id
    '''
    active_product = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    db_active_product = await db.scalars(active_product)
    res_active_product = db_active_product.first()
    if res_active_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found or inactive')
    active_category = select(CategoryModel.id).where(CategoryModel.id == res_active_product.category_id,
                                                     CategoryModel.is_active == True)
    db_active_category = await db.scalars(active_category)
    if db_active_category.first() is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category not found or inactive')

    await db.execute(
        update(ProductModel).where(ProductModel.id == product_id).values(**new_product.model_dump())
    )
    await db.commit()
    await db.refresh(res_active_product)
    return res_active_product


@router.delete('/{product_id}', status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    '''
    To delete a product by product_id making it inactive
    '''
    active_product = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    db_active_product = await db.scalars(active_product)
    res_active_product = db_active_product.first()
    if res_active_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found or inactive')

    res_active_product.is_active = False
    await db.commit()
    return {"status": "success", "message": "Product marked as inactive"}
