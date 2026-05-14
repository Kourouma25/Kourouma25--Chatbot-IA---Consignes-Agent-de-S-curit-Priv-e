from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    password: str
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    email: str
    user_id: int