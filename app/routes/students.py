from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student, FaceEmbedding
from app.schemas import StudentCreate, StudentResponse

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student, FaceEmbedding

from app.services.face_embedding_service import (
    FaceEmbeddingService
)

from sqlalchemy import exists


router = APIRouter(
    prefix="/api/students",
    tags=["Students"]
)


# ============================================================
# CREATE STUDENT
# ============================================================

@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Check duplicate roll number
    # --------------------------------------------------------

    if student_data.roll_number:

        existing_student = (
            db.query(Student)
            .filter(
                Student.roll_number == student_data.roll_number
            )
            .first()
        )

        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Student with this roll number already exists"
            )

    # --------------------------------------------------------
    # Check duplicate email
    # --------------------------------------------------------

    if student_data.email:

        existing_student = (
            db.query(Student)
            .filter(
                Student.email == student_data.email
            )
            .first()
        )

        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Student with this email already exists"
            )

    # --------------------------------------------------------
    # Create student
    # --------------------------------------------------------

    student = Student(
        name=student_data.name,
        email=student_data.email,
        roll_number=student_data.roll_number,
        department=student_data.department,
        semester=student_data.semester
    )

    # --------------------------------------------------------
    # Save student
    # --------------------------------------------------------

    try:

        db.add(student)
        db.commit()
        db.refresh(student)

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student with this roll number or email already exists"
        )

    # --------------------------------------------------------
    # Return created student
    # --------------------------------------------------------

    return StudentResponse(
        id=student.id,
        name=student.name,
        email=student.email,
        roll_number=student.roll_number,
        department=student.department,
        semester=student.semester,
        is_active=student.is_active,
        face_enrolled=False  # New student won't have face enrolled yet,
    )


# ============================================================
# GET ALL STUDENTS
# ============================================================

@router.get(
    "/",
    response_model=list[StudentResponse]
)
def get_students(
    db: Session = Depends(get_db)
):

    students = (
      db.query(
        Student,
        exists().where(
            FaceEmbedding.student_id == Student.id
        ).label("face_enrolled"),
      )
      .order_by(Student.id.desc())
      .all()
    )

    result = []

    for student, face_enrolled in students:

        result.append(
            {
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "roll_number": student.roll_number,
            "department": student.department,
            "semester": student.semester,
            "is_active": student.is_active,
            "face_enrolled": bool(face_enrolled),
            }
        )

    return result


# ============================================================
# GET STUDENT BY DATABASE ID
# ============================================================

@router.get(
    "/{student_id}",
    response_model=StudentResponse
)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):

    student = (
        db.query(Student)
        .filter(
            Student.id == student_id
        )
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return student

# ============================================================
# ENROLL STUDENT FACE EMBEDDINGS
# ============================================================

MIN_VALID_EMBEDDINGS = 10
MAX_IMAGES_PER_ENROLLMENT = 20


@router.post(
    "/{student_id}/face-embeddings",
    status_code=status.HTTP_201_CREATED
)
async def create_face_embeddings(
    student_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):

    # ========================================================
    # 1. FIND STUDENT
    # ========================================================
    print("Finding student with ID:", student_id)
    student = (
        db.query(Student)
        .filter(
            Student.id == student_id,
            Student.is_active == True
        )
        .first()
    )

    if not student:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active student not found"
        )

    # ========================================================
    # Check existing face enrollment
    # ========================================================
    existing_embedding = (
        db.query(FaceEmbedding)
        .filter(
            FaceEmbedding.student_id == student_id
        )
        .first()
    )

    if existing_embedding:
        raise HTTPException(
            status_code=409,
            detail="Face already enrolled for this student",
        )

    # ========================================================
    # 2. VALIDATE NUMBER OF FILES
    # ========================================================

    if len(files) == 0:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one image is required"
        )

    if len(files) > MAX_IMAGES_PER_ENROLLMENT:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Maximum {MAX_IMAGES_PER_ENROLLMENT} "
                "images are allowed"
            )
        )

    # ========================================================
    # 3. PROCESS IMAGES
    # ========================================================

    generated_embeddings = []
    failed_images = []

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    for file in files:

        # ----------------------------------------------------
        # Validate content type
        # ----------------------------------------------------

        if file.content_type not in allowed_types:

            failed_images.append({
                "filename": file.filename,
                "reason": "Unsupported image format"
            })

            continue

        # ----------------------------------------------------
        # Read image
        # ----------------------------------------------------

        try:

            image_bytes = await file.read()

        except Exception:

            failed_images.append({
                "filename": file.filename,
                "reason": "Could not read image"
            })

            continue

        # ----------------------------------------------------
        # Check empty file
        # ----------------------------------------------------

        if not image_bytes:

            failed_images.append({
                "filename": file.filename,
                "reason": "Empty image file"
            })

            continue

        # ----------------------------------------------------
        # Generate embedding
        # ----------------------------------------------------

        try:

            embedding = (
                FaceEmbeddingService.generate_embedding(
                    image_bytes
                )
            )

            generated_embeddings.append({
                "filename": file.filename,
                "embedding": embedding
            })

        except ValueError as error:

            failed_images.append({
                "filename": file.filename,
                "reason": str(error)
            })

        except Exception:

            failed_images.append({
                "filename": file.filename,
                "reason": "Unexpected processing error"
            })

    # ========================================================
    # 4. CHECK MINIMUM VALID EMBEDDINGS
    # ========================================================

    valid_count = len(generated_embeddings)

    if valid_count < MIN_VALID_EMBEDDINGS:

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Nothing has been inserted into the database yet.
        #
        # Therefore this enrollment is completely rejected.
        # ----------------------------------------------------

        return {
            "success": False,
            "message": (
                "Enrollment rejected. "
                f"At least {MIN_VALID_EMBEDDINGS} "
                "valid face images are required."
            ),

            "student": {
                "id": student.id,
                "name": student.name
            },

            "images_uploaded": len(files),

            "valid_images": valid_count,

            "failed_images_count": len(
                failed_images
            ),

            "minimum_required": MIN_VALID_EMBEDDINGS,

            "enrollment_completed": False,

            "failed_images": failed_images
        }

    # ========================================================
    # 5. SAVE ALL VALID EMBEDDINGS
    # ========================================================

    try:

        for item in generated_embeddings:

            face_embedding = FaceEmbedding(
                student_id=student.id,
                embedding=item["embedding"],
                model_name="face_recognition",
                model_version="v1"
            )

            db.add(face_embedding)

        # ----------------------------------------------------
        # Commit everything together
        # ----------------------------------------------------

        db.commit()

    except Exception:

        # ----------------------------------------------------
        # Rollback everything if database operation fails
        # ----------------------------------------------------

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save face embeddings"
        )

    # ========================================================
    # 6. SUCCESS RESPONSE
    # ========================================================

    return {
        "success": True,

        "message": (
            "Student face enrollment completed successfully"
        ),

        "student": {
            "id": student.id,
            "name": student.name
        },

        "images_uploaded": len(files),

        "valid_images": valid_count,

        "failed_images_count": len(
            failed_images
        ),

        "embeddings_created": valid_count,

        "minimum_required": MIN_VALID_EMBEDDINGS,

        "enrollment_completed": True,

        "failed_images": failed_images
    }