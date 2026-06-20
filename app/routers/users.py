from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.data.db import SessionDep
from app.models.user import User
from app.models.registration import Registration


router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def get_users(session: SessionDep):
    """
    Restituisce tutti gli utenti presenti nel database.
    """
    return session.exec(select(User)).all()


@router.post("", status_code=201)
def create_user(user: User, session: SessionDep):
    """
    Crea un nuovo utente.
    """
    existing_user = session.get(User, user.username)

    if existing_user is not None:
        raise HTTPException(status_code=400, detail="User already exists")

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.get("/{username}")
def get_user(username: str, session: SessionDep):
    """
    Restituisce un utente dato il suo username.
    """
    user = session.get(User, username)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.delete("")
def delete_all_users(session: SessionDep):
    """
    Elimina tutti gli utenti e tutte le registrazioni associate.
    """
    registrations = session.exec(select(Registration)).all()

    for registration in registrations:
        session.delete(registration)

    users = session.exec(select(User)).all()

    for user in users:
        session.delete(user)

    session.commit()

    return {"message": "All users deleted"}


@router.delete("/{username}")
def delete_user(username: str, session: SessionDep):
    """
    Elimina un utente e tutte le sue registrazioni.
    """
    user = session.get(User, username)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    registrations = session.exec(
        select(Registration).where(Registration.username == username)
    ).all()

    for registration in registrations:
        session.delete(registration)

    session.delete(user)
    session.commit()

    return {"message": "User deleted"}