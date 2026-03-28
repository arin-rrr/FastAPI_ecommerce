from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.users import User as UserModel
from app.config import SECRET_KEY, ALGORITHM
from app.db_depends import get_async_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # время действия access-токена
REFRESH_TOKEN_EXPIRE_DAYS = 7  # время действия refresh-токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")  # время действия созданного токена


def hash_password(password: str) -> str:
    """
    Пароль в хеш с использованием bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли введённый пароль сохранённому хешу.
    """
    return pwd_context.verify(plain_password, hashed_password)


'''
Именно эта функция будет использоваться в эндпоинте логина (POST /token) для выдачи токена после успешной аутентификации.
'''


def create_access_token(data: dict):
    """
    Создаёт JWT с payload (sub, role, id, exp) -> email, role, ID и время истечения.
    """
    to_encode = data.copy()  # создаёт копию текущего словаря с параметрами
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # задаёт, через какое время токен истечёт
    to_encode.update({"exp": expire, 'token_type': 'access'})  # Добавляет поле exp (expiration) в payload токена
    '''
    Кодирует данные в JWT с SECRET_KEY и алгоритма подписи. В итоге возвращает строку токена, состоящую из Header, 
    Payload и Signature, разделённых точками.
    '''
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    """
    Создаёт refresh-токен с длительным сроком действия и token_type="refresh".
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "token_type": "refresh",
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Функция проверки JWT и получения пользователя
async def get_current_user(token: str = Depends(oauth2_scheme),
                               db: AsyncSession = Depends(get_async_db)):
        """
        Проверяет JWT и возвращает пользователя из базы.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            token_type: str = payload.get("token_type")
            if email is None or token_type != "access":
                raise credentials_exception
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.PyJWTError:
            raise credentials_exception
        result = await db.scalars(
            select(UserModel).where(UserModel.email == email, UserModel.is_active == True))
        user = result.first()
        if user is None:
            raise credentials_exception
        return user


async def get_current_seller(current_user: UserModel = Depends(get_current_user)):
        '''
        Проверяет, что пользователь seller
        '''
        if current_user.role != 'seller':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only sellers can perform this action")
        return current_user


async def get_current_buyer(current_user: UserModel = Depends(get_current_user)):
        '''
        Проверяет, что пользователь buyer
        '''
        if current_user.role != 'buyer':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only buyers can perform this action')
        return current_user
