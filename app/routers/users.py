from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

from app.models.users import User as UserModel
from app.schema import UserCreate, User as UserSchema
from app.db_depends import get_async_db
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix='/users', tags=['users'])


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Регистрирует нового пользователя с ролью 'buyer' или 'seller'.
    """

    # Проверка уникальности email
    result = await db.scalars(select(UserModel).where(UserModel.email == user.email))
    if result.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already registered")

    # Создание объекта пользователя с хешированным паролем
    db_user = UserModel(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )

    # Добавление в сессию и сохранение в базе
    db.add(db_user)
    await db.commit()
    return db_user

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_async_db)):
    """
    Аутентифицирует пользователя и возвращает JWT с email, role и id.
    """
    result = await db.scalars(
        select(UserModel).where(UserModel.email == form_data.username, UserModel.is_active == True))
    user = result.first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}