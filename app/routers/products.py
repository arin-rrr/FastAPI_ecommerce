from fastapi import APIRouter

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


@router.post('/')
async def create_product():
    '''
    To create a new product
    '''
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
