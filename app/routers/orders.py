from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.db_depends import get_async_db
from app.models.cart_items import CartItem as CartItemModel
from app.models.orders import Order as OrderModel, OrderItem as OrderItemModel
from app.models.users import User as UserModel
from app.schema import Order as OrderSchema, OrderList

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


async def _load_order_with_items(db: AsyncSession, order_id: int) -> OrderModel | None:
    result = await db.scalars(
        select(OrderModel)
        .options(
            selectinload(OrderModel.items).selectinload(OrderItemModel.product),
        )
        .where(OrderModel.id == order_id)
    )
    return result.first()


@router.get('/checkout', response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def checkout_order(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_user),
):
    """
    Создаёт заказ на основе текущей корзины пользователя.
    Сохраняет позиции заказа, вычитает остатки и очищает корзину.
    """

    '''
    Текущее состояние корзины получаем
    '''
    cart_result = await db.scalars(
        select(CartItemModel)
        .options(selectinload(CartItemModel.product))
        .where(CartItemModel.user_id == current_user.id)
        .order_by(CartItemModel.id)
    )

    '''
    Проверяем, что корзина не пустая, иначе ошибка
    '''
    cart_items = cart_result.all()
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    '''
    Создаём заказ и начинаем проходиться по товарам
    '''
    order = OrderModel(user_id=current_user.id)
    total_amount = Decimal("0")

    for cart_item in cart_items:
        product = cart_item.product

        '''
        Проверяем, что товары активны и их достаточно для заказа
        '''
        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {cart_item.product_id} is unavailable",
            )
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for product {product.name}",
            )

        '''
        Фиксируем цену и считаем общую стоимость корзины
        '''
        unit_price = product.price
        if unit_price is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product.name} has no price set",
            )
        total_price = unit_price * cart_item.quantity
        total_amount += total_price

        '''
        Уменьшаем остатки
        '''
        order_item = OrderItemModel(
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            unit_price=unit_price,
            total_price=total_price,
        )
        order.items.append(order_item)

        product.stock -= cart_item.quantity

    '''
    Сохраняем заказ и очищаем корзину
    '''
    order.total_amount = total_amount
    db.add(order)

    await db.execute(delete(CartItemModel).where(CartItemModel.user_id == current_user.id))
    await db.commit()

    '''
    Перезагружаем заказ с полными данными
    '''
    created_order = await _load_order_with_items(db, order.id)
    if not created_order:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load created order",
        )
    return created_order
