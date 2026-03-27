from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_seller
from app.db_depends import get_async_db

from app.schema import Product as ProductSchema, ProductCreate, UserCreate, ReviewCreate
from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.models.reviews import Reviews as ReviewsModel

router = APIRouter('/reviews', tags=['reviews'])


@router.get('/')
async def get_all_reviews(db: AsyncSession = Depends(get_async_db), status_code=status.HTTP_200_OK):
    '''
    Get all active reviews
    '''
    db_results = await db.scalars(select(ReviewsModel).where(ReviewsModel.is_active == True))
    return db_results.all()


@router.post('/', response_model=ReviewsModel, status_code=status.HTTP_201_CREATED)
async def add_review(review: ReviewCreate, db: AsyncSession = Depends(get_async_db),
                     current_user: UserCreate = Depends(get_current_buyer)):
    '''
    Добавление нового отзыва для продукта и перерасчёт среднего рейтинга товара
    '''
