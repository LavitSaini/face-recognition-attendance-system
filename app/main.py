from sqlalchemy import text

from fastapi import FastAPI

from .database import engine

from app.routes.students import router as students_router
from app.routes.attendence import router as attendance_router
from app.routes.recognition import router as recognition_router
from app.routes.teachers import router as teachers_router

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Face Attendance System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://class-face.netlify.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students_router)
app.include_router(attendance_router)
app.include_router(recognition_router)
app.include_router(teachers_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Face Attendance API is running"
    }


@app.get("/health/database")
def database_health_check():

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT 1")
            )

            result.scalar()

        return {
            "status": "ok",
            "database": "connected"
        }

    except Exception as error:

        return {
            "status": "error",
            "database": "connection failed",
            "detail": str(error)
        }