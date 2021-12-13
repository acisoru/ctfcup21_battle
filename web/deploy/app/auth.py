from logging import log
import uuid
from typing import Optional, Union
from datetime import datetime, timedelta

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from loguru import logger

from . import db
from .settings import settings


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel()  # password={"tokenUrl": tokenUrl, "scopes": scopes}
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: Optional[str] = request.cookies.get("access_token")

        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No cookie",
                headers={"WWW-Authenticate": "Bearer"},
            )

        scheme, param = get_authorization_scheme_param(authorization)
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_user_token(user: db.User):
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user": str(
                user.username,
            )
        },
        expires_delta=access_token_expires,
    )
    return access_token


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id: Union[str, None] = None

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])  # no "alg:none"
        user_id = payload.get("user")
        if user_id is None:
            raise credentials_exception
    except JWTError as ex:
        logger.info(f"e={ex}")
        raise credentials_exception

    user = await db.DB().find(login=user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_safe(request: Request) -> Optional[db.User]:
    user = None
    try:
        user = await get_current_user(await oauth2_scheme(request))
    except HTTPException as ex:
        user = None
    return user
