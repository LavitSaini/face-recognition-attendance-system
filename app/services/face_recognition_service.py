import numpy as np
import face_recognition

from sqlalchemy.orm import Session

from app.models import FaceEmbedding, Student


class FaceRecognitionService:
    # ============================================================
    # RECOGNITION THRESHOLD
    # ============================================================

    RECOGNITION_THRESHOLD = 0.50

    # ============================================================
    # FIND BEST MATCH
    # ============================================================

    @staticmethod
    def recognize_face(
        db: Session,
        live_embedding: list[float],
    ):
        """
        Compare one live face embedding against
        all active students' stored embeddings.

        Returns:
            {
                "student_id": int,
                "name": str,
                "distance": float,
            }

        or None if no face matches.
        """

        # --------------------------------------------------------
        # Convert live embedding to numpy array
        # --------------------------------------------------------

        live_embedding_array = np.asarray(
            live_embedding,
            dtype=np.float64,
        )

        # --------------------------------------------------------
        # Load stored embeddings
        # --------------------------------------------------------

        records = (
            db.query(FaceEmbedding, Student)
            .join(
                Student,
                FaceEmbedding.student_id == Student.id,
            )
            .filter(
                Student.is_active.is_(True),
            )
            .all()
        )

        # --------------------------------------------------------
        # No enrolled faces
        # --------------------------------------------------------

        if not records:
            return None

        # --------------------------------------------------------
        # Prepare embeddings
        # --------------------------------------------------------

        known_embeddings = []
        students = []

        for face_embedding, student in records:
            embedding = np.asarray(
                face_embedding.embedding,
                dtype=np.float64,
            )

            # ----------------------------------------------------
            # Validate embedding dimension
            # ----------------------------------------------------

            if embedding.shape != live_embedding_array.shape:
                continue

            known_embeddings.append(embedding)
            students.append(student)

        # --------------------------------------------------------
        # No valid embeddings
        # --------------------------------------------------------

        if not known_embeddings:
            return None

        # --------------------------------------------------------
        # Calculate distances
        # --------------------------------------------------------

        distances = face_recognition.face_distance(
            known_embeddings,
            live_embedding_array,
        )

        # --------------------------------------------------------
        # Find closest embedding
        # --------------------------------------------------------

        best_match_index = int(
            np.argmin(distances),
        )

        best_distance = float(
            distances[best_match_index],
        )

        best_student = students[best_match_index]

        # --------------------------------------------------------
        # Apply recognition threshold
        # --------------------------------------------------------

        if (
            best_distance
            >= FaceRecognitionService.RECOGNITION_THRESHOLD
        ):
            return None

        # --------------------------------------------------------
        # Return recognized student
        # --------------------------------------------------------

        return {
            "student_id": best_student.id,
            "name": best_student.name,
            "distance": best_distance,
        }

        # ============================================================
    # LOAD KNOWN FACES FROM DATABASE
    # ============================================================

    @staticmethod
    def load_known_faces(db: Session):
        """
        Load all active students and their face embeddings
        from the database.

        This should be called once when an attendance session starts,
        rather than querying the database for every camera frame.

        Returns:
            (
                known_embeddings,
                known_students
            )
        """

        records = (
            db.query(FaceEmbedding, Student)
            .join(
                Student,
                FaceEmbedding.student_id == Student.id,
            )
            .filter(
                Student.is_active.is_(True),
            )
            .all()
        )

        known_embeddings = []
        known_students = []

        for face_embedding, student in records:

            embedding = np.asarray(
                face_embedding.embedding,
                dtype=np.float64,
            )

            # Face-recognition embeddings must contain 128 values.
            if embedding.shape != (128,):
                continue

            known_embeddings.append(
                embedding
            )

            known_students.append(
                {
                    "id": student.id,
                    "name": student.name,
                }
            )

        return (
            known_embeddings,
            known_students,
        )

    # ============================================================
    # RECOGNIZE USING ALREADY LOADED EMBEDDINGS
    # ============================================================

    @staticmethod
    def recognize_from_known_faces(
        live_embedding,
        known_embeddings,
        known_students,
    ):
        """
        Compare a live face embedding against embeddings
        that have already been loaded into memory.

        No database query is performed here.
        """

        if not known_embeddings:
            return None

        live_embedding = np.asarray(
            live_embedding,
            dtype=np.float64,
        )

        # --------------------------------------------------------
        # Validate live embedding
        # --------------------------------------------------------

        if live_embedding.shape != (128,):
            return None

        # --------------------------------------------------------
        # Calculate distances
        # --------------------------------------------------------

        distances = face_recognition.face_distance(
            known_embeddings,
            live_embedding,
        )

        # --------------------------------------------------------
        # Find closest face
        # --------------------------------------------------------

        best_match_index = int(
            np.argmin(distances)
        )

        best_distance = float(
            distances[best_match_index]
        )

        # --------------------------------------------------------
        # Apply recognition threshold
        # --------------------------------------------------------

        if (
            best_distance
            >= FaceRecognitionService.RECOGNITION_THRESHOLD
        ):
            return None

        # --------------------------------------------------------
        # Get matched student
        # --------------------------------------------------------

        student = known_students[
            best_match_index
        ]

        # --------------------------------------------------------
        # Return result
        # --------------------------------------------------------

        return {
            "student_id": student["id"],
            "name": student["name"],
            "distance": best_distance,
        }