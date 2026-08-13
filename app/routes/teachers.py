from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.config import (
    TEACHER_REGISTRATION_KEY,
)
from app.utility import (
    create_access_token,
    hash_password,
    verify_password,
    get_current_teacher
)
from app.database import get_db
from app.models import Teacher
from app.schemas import (
    TeacherLoginRequest,
    TeacherLoginResponse,
    TeacherRegisterRequest,
    TeacherResponse,
)



router = APIRouter(
    prefix="/api/auth/teachers",
    tags=["Teacher Authentication"],
)

@router.post(
    "/register",
    response_model=TeacherResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_teacher(
    data: TeacherRegisterRequest,
    db: Session = Depends(get_db),
):

    # ========================================================
    # 1. VALIDATE PRIVATE REGISTRATION KEY
    # ========================================================

    if not TEACHER_REGISTRATION_KEY:
        raise HTTPException(
            status_code=500,
            detail=(
                "Teacher registration key "
                "is not configured."
            ),
        )

    if (
        data.registration_key
        != TEACHER_REGISTRATION_KEY
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid teacher registration key.",
        )


    # ========================================================
    # 2. CHECK EXISTING EMAIL
    # ========================================================

    existing_teacher = (
        db.query(Teacher)
        .filter(
            Teacher.email == data.email
        )
        .first()
    )

    if existing_teacher:

        raise HTTPException(
            status_code=409,
            detail="Teacher account already exists.",
        )


    # ========================================================
    # 3. CREATE TEACHER
    # ========================================================

    teacher = Teacher(
        name=data.name,
        email=data.email,
        password_hash=hash_password(
            data.password
        ),
        is_active=True,
    )

    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return teacher


@router.post(
    "/login",
    response_model=TeacherLoginResponse,
)
def login_teacher(
    data: TeacherLoginRequest,
    db: Session = Depends(get_db),
):

    # ========================================================
    # 1. FIND TEACHER
    # ========================================================

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.email == data.email
        )
        .first()
    )

    if teacher is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )


    # ========================================================
    # 2. CHECK PASSWORD
    # ========================================================

    if not verify_password(
        data.password,
        teacher.password_hash,
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )


    # ========================================================
    # 3. CHECK ACCOUNT STATUS
    # ========================================================

    if not teacher.is_active:

        raise HTTPException(
            status_code=403,
            detail="Teacher account is inactive.",
        )


    # ========================================================
    # 4. CREATE JWT
    # ========================================================

    access_token = create_access_token(
        teacher.id
    )


    return {
        "access_token": access_token,
        "token_type": "bearer",
        "teacher": teacher,
    }

@router.get("/me")
def get_current_teacher_info(
    current_teacher: Teacher = Depends(
        get_current_teacher
    ),
):
    return {
        "id": current_teacher.id,
        "name": current_teacher.name,
        "email": current_teacher.email,
        "is_active": current_teacher.is_active,
    }