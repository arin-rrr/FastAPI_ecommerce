from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_seller
from app.db_depends import get_db, get_async_db
from app.schema import Product as ProductSchema, ProductCreate, UserCreate, ReviewResponse
from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.models.reviews import Reviews as ReviewsModel

router = APIRouter(
    prefix='/products',
    tags=['products']
)


@router.get('/')
async def get_all_products(db: AsyncSession = Depends(get_async_db), status_code=status.HTTP_200_OK):
    '''
    To get the list of all products
    '''
    # перепишу в две строчки
    db_result = await db.scalars(select(ProductModel).where(ProductModel.is_active == True))
    return db_result.all()


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
        product: ProductCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserCreate = Depends(get_current_seller)
):
    """
    Создаёт новый товар, привязанный к текущему продавцу (только для 'seller').
    """
    category_result = await db.scalars(
        select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active == True)
    )
    if not category_result.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")
    db_product = ProductModel(**product.model_dump(), seller_id=current_user.id, rating=0.0)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)  # Для получения id и is_active из базы
    return db_product


@router.get('/category/{category_id}', status_code=status.HTTP_200_OK, response_model=list[ProductSchema])
async def get_product_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)) -> list[ProductSchema]:
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
async def get_product_info_by_id(product_id: int, db: AsyncSession = Depends(get_async_db)) -> ProductSchema:
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

    product_by_id = select(ProductModel.category_id).where(ProductModel.is_active == True,
                                                           ProductModel.id == product_id)
    db_category_product_by_id = await db.scalars(product_by_id)
    if db_category_product_by_id.first() not in res_active_categories:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category not found or inactive')
    return res_active_product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
        product_id: int,
        product: ProductCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserCreate = Depends(get_current_seller)
):
    """
    Обновляет товар, если он принадлежит текущему продавцу (только для 'seller').
    """
    result = await db.scalars(select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True))
    db_product = result.first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own products")
    category_result = await db.scalars(
        select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active == True)
    )
    if not category_result.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")
    await db.execute(
        update(ProductModel).where(ProductModel.id == product_id).values(**product.model_dump())
    )
    await db.commit()
    await db.refresh(db_product)  # Для консистентности данных
    return db_product


@router.delete("/{product_id}", response_model=ProductSchema)
async def delete_product(
        product_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserCreate = Depends(get_current_seller)
):
    """
    Выполняет мягкое удаление товара, если он принадлежит текущему продавцу (только для 'seller').
    """
    result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    )
    product = result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own products")
    await db.execute(
        update(ProductModel).where(ProductModel.id == product_id).values(is_active=False)
    )
    await db.commit()
    await db.refresh(product)  # Для возврата is_active = False
    return product


@router.get('/{product_id}/reviews', response_model=list[ReviewResponse])
async def get_reviews_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    )
    product = result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    reviews = await db.scalars(select(ReviewsModel).where(ReviewsModel.product_id == product.id))
    reviews_result = reviews.all()
    return reviews_result