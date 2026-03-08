from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db
from app.models.categories import Category as CategoryModel
from app.schema import Category as CategorySchema, CategoryCreate

router = APIRouter(
    prefix='/categories',
    tags=['categories']
)


# делаем наброски
@router.get('/', response_model=list[CategorySchema])
async def get_all_categories(db: AsyncSession = Depends(get_async_db)):
    '''
    To get the list of all active categories
    '''
    result = await db.scalars(select(CategoryModel).where(CategoryModel.is_active == True))
    categories = result.all()
    return categories


@router.post('/', response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_async_db)):
    '''
    To create a new category
    '''

    # проверка существования и корректности parent_id
    if category.parent_id is not None:
        stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id, CategoryModel.is_active == True)
        result = await db.scalars(stmt)
        parent = result.first()
        if parent is None: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                               detail='Parent category is not found')

    # создания новой категории
    new_category = CategoryModel(**category.model_dump())
    db.add(new_category)
    await db.commit()
    return new_category


@router.put('/{category_id}')
async def update_category(category_id: int, category: CategoryCreate, db: AsyncSession = Depends(get_async_db)):
    '''
    To update a category by ID - name or parent_id
    '''

    # проверяем, что категория существует
    stmt = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    new_category = result.first()
    if new_category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category not found')

    # проверяем корректность parent_id
    if category.parent_id is not None:
        parent_stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id,
                                                  CategoryModel.is_active == True)
        parent_result = await db.scalars(parent_stmt)
        parent = parent_result.first()
        if parent is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect parent_id')
        if parent.id == category_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category cannot be its own parent")
    update_data = category.model_dump(exclude_unset=True)
    await db.execute(
        update(CategoryModel).where(CategoryModel.id == category_id).values(**update_data)
    )
    await db.commit()
    return new_category


@router.delete('/{category_id}', status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    '''
    To "delete" a category by ID by making it inactive
    '''
    stmt = select(CategoryModel).where(CategoryModel.is_active == True, CategoryModel.id == category_id)
    result = await db.scalars(stmt)
    category = result.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')

    await db.execute(update(CategoryModel).where(CategoryModel.id == category_id).values(is_active=False))
    await db.commit()
    return category
