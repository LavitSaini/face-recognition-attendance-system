from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.services.face_embedding_service import (
    FaceEmbeddingService
)
from app.services.face_recognition_service import (
    FaceRecognitionService
)


router = APIRouter(
    prefix="/api/recognition",
    tags=["Recognition"]
)


# ============================================================
# RECOGNIZE FACE FROM IMAGE
# ============================================================

@router.post("/recognize")
async def recognize_face(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Validate image type
    # --------------------------------------------------------

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    if file.content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail="Unsupported image format"
        )

    # --------------------------------------------------------
    # Read image
    # --------------------------------------------------------

    image_bytes = await file.read()

    if not image_bytes:

        raise HTTPException(
            status_code=400,
            detail="Empty image file"
        )

    # --------------------------------------------------------
    # Generate live face embedding
    # --------------------------------------------------------

    try:

        live_embedding = (
            FaceEmbeddingService.generate_embedding(
                image_bytes
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    # --------------------------------------------------------
    # Recognize against NeonDB embeddings
    # --------------------------------------------------------

    result = (
        FaceRecognitionService.recognize_face(
            db,
            live_embedding
        )
    )

    # --------------------------------------------------------
    # Unknown face
    # --------------------------------------------------------

    if result is None:

        return {
            "recognized": False,
            "message": "Unknown face"
        }

    # --------------------------------------------------------
    # Recognized face
    # --------------------------------------------------------

    return {
        "recognized": True,
        "student": {
            "id": result["student_id"],
            "name": result["name"]
        },
        "distance": result["distance"]
    }