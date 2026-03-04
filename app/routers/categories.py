from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.categories import Category as CategoryModel
from app.schema import Category as CategorySchema, CategoryCreate
from app.db_depends import get_db

router = APIRouter(
    prefix='/categories',
    tags=['categories']
)


# делаем наброски (заглушки)
@router.get('/')
async def get_all_categories():
    '''
    To get the list of all categories
    '''
    return {'message': 'Список всех категорий.'}


@router.post('/', response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    '''
    To create a new category
    '''

    # проверка существования и корректности parent_id
    if category.parent_id is not None:
        stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id, CategoryModel.is_active == True)
        parent = db.scalars(stmt).first()
        if parent is None: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Parent category is not found')

    # создания новой категории
    new_category = CategoryModel(**category.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.put('/{category_id}')
async def update_category(category_id: int):
    '''
    To update a category by ID
    '''
    return {'message': f'Категория с {category_id} обновлена.'}

@router.delete('/{category_id}')
async def delete_category(category_id: int):
    '''
    To delete a category by ID
    '''
    return {'message': f'Категория с {category_id} удалена.'}