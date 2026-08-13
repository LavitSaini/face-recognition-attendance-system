from pydantic import BaseModel, EmailStr


class StudentCreate(BaseModel):
    name: str
    email: EmailStr | None = None
    roll_number: str | None = None
    department: str | None = None
    semester: int | None = None


class StudentResponse(BaseModel):
    id: int
    name: str
    email: str | None = None
    roll_number: str | None = None
    department: str | None = None
    semester: int | None = None
    is_active: bool
    face_enrolled: bool

    class Config:
        from_attributes = True


class TeacherRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    registration_key: str


class TeacherLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TeacherResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool


class TeacherLoginResponse(BaseModel):
    access_token: str
    token_type: str
    teacher: TeacherResponse