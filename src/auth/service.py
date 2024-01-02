from __future__ import annotations
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict

from pydantic import UUID4
from sqlalchemy import insert, select

import utils
from auth.config import auth_config
from auth.exceptions import InvalidCredentials
from auth.schemas import AuthUser
from auth.security import check_password, hash_password
from models import AuthTable, execute, fetch_one, RefreshTokens


async def create_user(user: AuthUser) -> Dict[str, Any] | None:
    insert_query = (
        insert(AuthTable)
        .values(
            {
                "email": user.email,
                "password": hash_password(user.password),
                "created_at": datetime.utcnow(),
            }
        )
        .returning(AuthTable)
    )

    return await fetch_one(insert_query)


async def get_user_by_id(user_id: int) -> Dict[str, Any] | None:
    select_query = select(AuthTable).where(AuthTable.c.id == user_id)

    return await fetch_one(select_query)


async def get_user_by_email(email: str) -> Dict[str, Any] | None:
    select_query = select(AuthTable).where(AuthTable.c.email == email)

    return await fetch_one(select_query)


async def create_refresh_token(
    *, user_id: int, refresh_token: str = None
) -> str:
    if not refresh_token:
        refresh_token = utils.generate_random_alphanum(64)

    insert_query = RefreshTokens.insert().values(
        uuid=uuid.uuid4(),
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(seconds=auth_config.REFRESH_TOKEN_EXP),
        user_id=user_id,
    )
    await execute(insert_query)

    return refresh_token


async def get_refresh_token(refresh_token: str) -> Dict[str, Any] | None:
    select_query = RefreshTokens.select().where(
        RefreshTokens.c.refresh_token == refresh_token
    )

    return await fetch_one(select_query)


async def expire_refresh_token(refresh_token_uuid: UUID4) -> None:
    update_query = (
        RefreshTokens.update()
        .values(expires_at=datetime.utcnow() - timedelta(days=1))
        .where(RefreshTokens.c.uuid == refresh_token_uuid)
    )

    await execute(update_query)


async def authenticate_user(auth_data: AuthUser) -> Dict[str, Any]:
    user = await get_user_by_email(auth_data.email)
    if not user:
        raise InvalidCredentials()

    if not check_password(auth_data.password, user["password"]):
        raise InvalidCredentials()

    return user