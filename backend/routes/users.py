from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Utilisateur, Role
from backend.schemas import UserCreate
from backend.auth import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/create")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(Utilisateur).filter(
        Utilisateur.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email déjà utilisé"
        )

    role = db.query(Role).filter(
        Role.nom_role == user.role
    ).first()

    if not role:
        raise HTTPException(
            status_code=400,
            detail="Rôle invalide. Utilisez agent ou responsable."
        )

    new_user = Utilisateur(
        nom=user.nom,
        prenom=user.prenom,
        email=user.email,
        mot_de_passe=hash_password(user.password),
        role_id=role.id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Utilisateur créé avec succès",
        "id": new_user.id,
        "email": new_user.email,
        "role": role.nom_role
    }


@router.get("/")
def list_users(db: Session = Depends(get_db)):
    users = db.query(Utilisateur).all()

    return [
        {
            "id": u.id,
            "nom": u.nom,
            "prenom": u.prenom,
            "email": u.email,
            "role": u.role.nom_role,
            "actif": u.actif
        }
        for u in users
    ]