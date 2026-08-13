from app.services.face_recognition_service import (
    FaceRecognitionService,
)


class AttendanceEngine:

    def __init__(
        self,
        known_embeddings,
        known_students,
    ):
        self.known_embeddings = known_embeddings
        self.known_students = known_students

        # Students already processed during this request/session.
        self.marked_students: set[int] = set()

    # ============================================================
    # RECOGNIZE FACE
    # ============================================================

    def recognize(
        self,
        live_embedding,
    ):
        return (
            FaceRecognitionService
            .recognize_from_known_faces(
                live_embedding=live_embedding,
                known_embeddings=self.known_embeddings,
                known_students=self.known_students,
            )
        )

    # ============================================================
    # CHECK WHETHER STUDENT WAS ALREADY PROCESSED
    # ============================================================

    def already_marked(
        self,
        student_id: int,
    ) -> bool:
        return student_id in self.marked_students

    # ============================================================
    # REMEMBER STUDENT
    # ============================================================

    def mark_as_processed(
        self,
        student_id: int,
    ) -> None:
        self.marked_students.add(student_id)