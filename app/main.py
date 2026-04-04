from fastapi import FastAPI
from app.routers import categories, products, users, reviews, cart, orders

app = FastAPI(
    title='Интернет-магазин на FastAPI',
    version='0.1.0'
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(reviews.router)
app.include_router(cart.router)
app.include_router(orders.router)


@app.get('/')
async def root():
    return {'message': 'Добро пожаловать в API интернет-магазина'}
