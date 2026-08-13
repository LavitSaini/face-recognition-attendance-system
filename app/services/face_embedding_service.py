import io

import face_recognition
import numpy as np
from PIL import Image


class FaceEmbeddingService:

    # ========================================================
    # GENERATE SINGLE EMBEDDING
    # Used during student enrollment
    # ========================================================

    @staticmethod
    def generate_embedding(
        image_bytes: bytes,
    ):
        """
        Generate one face embedding from an image.

        Enrollment requires exactly one face.
        """

        # ----------------------------------------------------
        # Convert bytes → PIL image
        # ----------------------------------------------------

        try:
            image = Image.open(
                io.BytesIO(image_bytes)
            ).convert("RGB")

        except Exception:
            raise ValueError(
                "Invalid image file"
            )

        # ----------------------------------------------------
        # Convert PIL image → NumPy array
        # ----------------------------------------------------

        image_array = np.array(image)

        # ----------------------------------------------------
        # Detect faces
        # ----------------------------------------------------

        face_locations = (
            face_recognition.face_locations(
                image_array,
                model="hog",
            )
        )

        # ----------------------------------------------------
        # No face
        # ----------------------------------------------------

        if len(face_locations) == 0:
            raise ValueError(
                "No face detected in image"
            )

        # ----------------------------------------------------
        # Multiple faces
        # ----------------------------------------------------

        if len(face_locations) > 1:
            raise ValueError(
                "Multiple faces detected. "
                "Only one face is allowed."
            )

        # ----------------------------------------------------
        # Generate 128-dimensional face encoding
        # ----------------------------------------------------

        encodings = (
            face_recognition.face_encodings(
                image_array,
                face_locations,
            )
        )

        if not encodings:
            raise ValueError(
                "Could not generate face encoding"
            )

        # ----------------------------------------------------
        # Return embedding
        # ----------------------------------------------------

        return encodings[0].tolist()

    # ========================================================
    # GENERATE MULTIPLE EMBEDDINGS
    # Used during attendance
    # ========================================================

    @staticmethod
    def generate_embeddings(
        image_bytes: bytes,
    ) -> list[list[float]]:
        """
        Generate embeddings for every face detected
        in an image.

        Unlike generate_embedding(), this method allows
        multiple faces.
        """

        # ----------------------------------------------------
        # Convert bytes → PIL image
        # ----------------------------------------------------

        try:
            image = Image.open(
                io.BytesIO(image_bytes)
            ).convert("RGB")

        except Exception:
            raise ValueError(
                "Invalid image file"
            )

        # ----------------------------------------------------
        # Convert PIL image → NumPy array
        # ----------------------------------------------------

        image_array = np.array(image)

        # ----------------------------------------------------
        # Detect ALL faces
        # ----------------------------------------------------

        face_locations = (
            face_recognition.face_locations(
                image_array,
                model="hog",
            )
        )

        # ----------------------------------------------------
        # No faces
        # ----------------------------------------------------

        if not face_locations:
            return []

        # ----------------------------------------------------
        # Generate embedding for every face
        # ----------------------------------------------------

        encodings = (
            face_recognition.face_encodings(
                image_array,
                face_locations,
            )
        )

        if not encodings:
            return []

        # ----------------------------------------------------
        # Convert NumPy arrays → Python lists
        # ----------------------------------------------------

        return [
            encoding.tolist()
            for encoding in encodings
        ]