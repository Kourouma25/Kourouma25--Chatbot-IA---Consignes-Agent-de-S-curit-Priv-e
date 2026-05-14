from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nom_role = Column(String(50), unique=True, nullable=False)

    utilisateurs = relationship("Utilisateur", back_populates="role")


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    mot_de_passe = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    actif = Column(Boolean, default=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())

    role = relationship("Role", back_populates="utilisateurs")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    nom_fichier = Column(String(255), nullable=False)
    chemin_fichier = Column(Text, nullable=False)
    type_fichier = Column(String(20))
    ajoute_par = Column(Integer, ForeignKey("utilisateurs.id"))
    date_ajout = Column(DateTime(timezone=True), server_default=func.now())


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    question = Column(Text, nullable=False)
    reponse = Column(Text)
    date_question = Column(DateTime(timezone=True), server_default=func.now())


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    note = Column(Integer)
    commentaire = Column(Text)
    date_feedback = Column(DateTime(timezone=True), server_default=func.now())