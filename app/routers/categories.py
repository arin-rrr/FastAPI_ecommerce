from fastapi import APIRouter

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


@router.post('/')
async def create_category():
    '''
    To create a new category
    '''
    return {'message': 'Новая категория создана.'}


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