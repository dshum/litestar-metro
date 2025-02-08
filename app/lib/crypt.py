from __future__ import annotations  # noqa: A005

import asyncio
import base64

from passlib.context import CryptContext

password_crypt_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_encryption_key(secret: str) -> bytes:
    if len(secret) <= 32:
        secret = f"{secret:<32}"[:32]
    return base64.urlsafe_b64encode(secret.encode())


async def get_password_hash(password: str | bytes) -> str:
    return await asyncio.get_running_loop().run_in_executor(None, password_crypt_context.hash, password)


async def verify_password(plain_password: str | bytes, hashed_password: str) -> bool:
    valid, _ = await asyncio.get_running_loop().run_in_executor(
        None,
        password_crypt_context.verify_and_update,
        plain_password,
        hashed_password,
    )
    return bool(valid)
