import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Union, Optional

from ..core import get_session, oauth2_scheme
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, desc, select
from ..models.user import Token, TokenData, CenterDirector, Teacher
from ..schemas import ErrorResponse, SuccessResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    dependencies=[Depends(get_session)],
    responses={404: {"description": "API Not found"}},
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM")
    )
    return encoded_jwt

def get_user_by_username(username: str, session: Session):
    statement = select(CenterDirector).where(CenterDirector.username == username)
    director = session.exec(statement).first()
    if director:
        return director
    statement = select(Teacher).where(Teacher.username == username)
    return session.exec(statement).first()


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/login", status_code=status.HTTP_200_OK, response_model=Union[SuccessResponse, ErrorResponse])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = get_user_by_username(form_data.username, session)

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return SuccessResponse(data={'access_token': access_token})
    # return Token(access_token=access_token, token_type="bearer")
