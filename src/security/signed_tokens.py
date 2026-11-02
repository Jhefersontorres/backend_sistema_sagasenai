import base64
import binascii
import hashlib
import hmac
import json
import time

from fastapi import HTTPException

from src.config import settings


def _encode_base64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _decode_base64(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_signed_token(claims: dict, expires_in_seconds: int) -> str:
    secret = settings.ADMIN_TOKEN_SECRET
    if not secret or len(secret) < 32:
        raise RuntimeError(
            "ADMIN_TOKEN_SECRET deve ter pelo menos 32 caracteres."
        )

    payload = {
        **claims,
        "exp": int(time.time()) + expires_in_seconds,
    }
    payload_base64 = _encode_base64(
        json.dumps(payload, separators=(",", ":")).encode()
    )
    signature = hmac.new(
        secret.encode(),
        payload_base64.encode(),
        hashlib.sha256,
    ).digest()
    return f"{payload_base64}.{_encode_base64(signature)}"


def verify_signed_token(token: str) -> dict:
    secret = settings.ADMIN_TOKEN_SECRET
    if not secret or len(secret) < 32:
        raise HTTPException(
            status_code=500,
            detail="ADMIN_TOKEN_SECRET ausente ou fraco.",
        )

    try:
        payload_base64, received_signature = token.split(".", 1)
        expected_signature = _encode_base64(
            hmac.new(
                secret.encode(),
                payload_base64.encode(),
                hashlib.sha256,
            ).digest()
        )
        if not hmac.compare_digest(received_signature, expected_signature):
            raise ValueError("Invalid token signature")

        payload = json.loads(_decode_base64(payload_base64).decode())
        if not isinstance(payload, dict):
            raise ValueError("Invalid token payload")
        if not isinstance(payload.get("exp"), int) or payload["exp"] <= time.time():
            raise ValueError("Expired or invalid token expiration")
        return payload
    except (
        ValueError,
        TypeError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        binascii.Error,
    ):
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado.",
        )
