from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.settings import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def ensure_authenticated(token: Annotated[str, Depends(oauth2_scheme)]) -> None:
    if token != get_settings().api_token:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
