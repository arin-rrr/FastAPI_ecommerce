from fastapi import FastAPI
from app.routers import categories

app = FastAPI(
    title='Интернет-магазин на FastAPI',
    version='0.1.0'
)

app.include_router(categories.router)


@app.get('/')
async def root():
    return {'message': 'Добро пожаловать в API интернет-магазина'}