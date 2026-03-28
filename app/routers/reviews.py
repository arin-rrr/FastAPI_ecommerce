from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_seller, get_current_buyer, get_current_user
from app.db_depends import get_async_db

from app.schema import Product as ProductSchema, ProductCreate, UserCreate, ReviewCreate
from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.models.users import User as UserModel
from app.models.reviews import Reviews as ReviewsModel

router = APIRouter(prefix='/reviews', tags=['reviews'])


@router.get('/')
async def get_all_reviews(db: AsyncSession = Depends(get_async_db), status_code=status.HTTP_200_OK):
    '''
    Get all active reviews
    '''
    db_results = await db.scalars(select(ReviewsModel).where(ReviewsModel.is_active == True))
    return db_results.all()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def add_review(
        review: ReviewCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_buyer)
):
    result = await db.execute(
        select(ProductModel).where(ProductModel.id == review.product_id, ProductModel.is_active == True)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    new_review = ReviewsModel(**review.model_dump(), user_id=current_user.id)
    db.add(new_review)

    # Получаем все старые оценки
    reviews_result = await db.execute(
        select(ReviewsModel.grade).where(
            ReviewsModel.product_id == review.product_id,
            ReviewsModel.is_active == True
        )
    )
    grades = list(reviews_result.scalars().all())

    grades.append(review.grade)

    new_rate = round(sum(grades) / len(grades), 1)

    product.rating = new_rate

    try:
        await db.commit()
        await db.refresh(new_review)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return new_review


@router.delete('/{review_id}')
async def delete_review(review_id: int, db: AsyncSession = Depends(get_async_db), current_user: UserCreate = Depends(get_current_user)):
    # Ищем активный отзыв по id
    db_reviews = await db.scalars(select(ReviewsModel).where(ReviewsModel.id == review_id, ReviewsModel.is_active == True))
    res_review = db_reviews.first()
    if res_review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Review not found or inactive')

    # Проверяем user'а
    if current_user.id != res_review.user_id and current_user.role not in ('buyer', 'admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to delete this review'
        )

    # Мягкое удаление
    res_review.is_active = False

    # Пересчёт grade'а
    all_reviews_products = await db.scalars(select(ReviewsModel.grade).where(ReviewsModel.is_active == True, ReviewsModel.product_id == res_review.product_id))
    grades = all_reviews_products.all()

    if not grades:
        new_rate = 0.0
    else:
        new_rate = sum(grades) / len(grades)

    await db.execute(update(ProductModel).where(ProductModel.id == res_review.product_id, ProductModel.is_active == True).values(rating=new_rate))
    await db.commit()
    return {'message': 'Review deleted'}
