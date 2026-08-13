import hashlib
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)
from app.database import get_db
from app.models import Teacher


# ============================================================
# OAUTH2
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/teachers/login"
)


# ============================================================
# PASSWORD HELPERS
# ============================================================

def _prepare_password(password: str) -> bytes:
    """
    Convert the password into a fixed-length SHA-256
    hexadecimal digest before passing it to bcrypt.

    This avoids bcrypt's 72-byte password limitation.
    """

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest().encode("utf-8")


def hash_password(password: str) -> str:
    """
    Hash a teacher password using:

        Password
            ↓
        SHA-256
            ↓
        bcrypt
            ↓
        Stored password hash
    """

    prepared_password = _prepare_password(
        password
    )

    password_hash = bcrypt.hashpw(
        prepared_password,
        bcrypt.gensalt(),
    )

    return password_hash.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against
    the stored bcrypt hash.
    """

    prepared_password = _prepare_password(
        plain_password
    )

    return bcrypt.checkpw(
        prepared_password,
        hashed_password.encode("utf-8"),
    )


# ============================================================
# JWT ACCESS TOKEN
# ============================================================

def create_access_token(
    teacher_id: int,
) -> str:
    """
    Create a JWT containing the authenticated
    teacher's ID.
    """

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(teacher_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


# ============================================================
# GET CURRENT AUTHENTICATED TEACHER
# ============================================================

def get_current_teacher(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Validate the JWT and return the authenticated teacher.

    Request
        ↓
    JWT
        ↓
    Decode token
        ↓
    Extract teacher ID
        ↓
    Find teacher in database
        ↓
    Return Teacher object
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate teacher credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    # ========================================================
    # DECODE JWT
    # ========================================================

    try:

        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

        teacher_id = payload.get("sub")

        if teacher_id is None:
            raise credentials_exception

        teacher_id = int(teacher_id)

    except (
        JWTError,
        ValueError,
        TypeError,
    ):

        raise credentials_exception


    # ========================================================
    # FIND TEACHER
    # ========================================================

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.id == teacher_id
        )
        .first()
    )


    # ========================================================
    # TEACHER NOT FOUND
    # ========================================================

    if teacher is None:

        raise credentials_exception


    # ========================================================
    # CHECK ACCOUNT STATUS
    # ========================================================

    if not teacher.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher account is inactive",
        )


    # ========================================================
    # RETURN AUTHENTICATED TEACHER
    # ========================================================

    return teacher