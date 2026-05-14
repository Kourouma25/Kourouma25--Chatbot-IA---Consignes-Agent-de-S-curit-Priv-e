from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Utilisateur
from backend.schemas import LoginRequest
from backend.auth import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(
        Utilisateur.email == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect"
        )

    if not verify_password(data.password, user.mot_de_passe):
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect"
        )

    if not user.actif:
        raise HTTPException(
            status_code=403,
            detail="Compte désactivé"
        )

    token = create_access_token({
        "sub": user.email,
        "role": user.role.nom_role,
        "user_id": user.id
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role.nom_role,
        "email": user.email,
        "user_id": user.id
    }