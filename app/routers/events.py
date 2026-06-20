from fastapi import APIRouter, HTTPException
from datetime import datetime
from sqlmodel import SQLModel, select

from app.data.db import SessionDep
from app.models.event import Event
from app.models.user import User
from app.models.registration import Registration


router = APIRouter(prefix="/events", tags=["events"])

class EventCreate(SQLModel):
    """
    Dati necessari per creare evento
    """
    
    title: str
    description: str
    date: datetime
    location: str


class UserCreate(SQLModel):
    """
    Dati necessari per registrare un utente a un evento.
    """

    username: str
    name: str
    email: str


@router.get("")
def get_events(session: SessionDep):
    """
    Restituisce tutti gli eventi presenti nel database.
    """
    return session.exec(select(Event)).all()


@router.post("", status_code=201)
def create_event(event_data: EventCreate, session: SessionDep):
    """
    Crea un nuovo evento.
    """
    event = Event(
        title=event_data.title,
        description=event_data.description,
        date=event_data.date,
        location=event_data.location,
        )
    session.add(event)
    session.commit()
    session.refresh(event)

    return event


@router.get("/{event_id}")
def get_event(event_id: int, session: SessionDep):
    """
    Restituisce un evento dato il suo id.
    """
    event = session.get(Event, event_id)

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


@router.put("/{event_id}")
def update_event(event_id: int, event_data: EventCreate, session: SessionDep):
    """
    Aggiorna un evento esistente.
    """
    event = session.get(Event, event_id)

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    event.title = event_data.title
    event.description = event_data.description
    event.date = event_data.date
    event.location = event_data.location

    session.add(event)
    session.commit()
    session.refresh(event)

    return event


@router.post("/{event_id}/register", status_code=201)
def register_to_event(event_id: int, user_data: UserCreate, session: SessionDep):
    """
    Registra un utente a un evento.
    Se l'utente non esiste, viene creato automaticamente.
    """
    event = session.get(Event, event_id)

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    user = session.get(User, user_data.username)

    if user is None:
        user = User(
            username=user_data.username,
            name=user_data.name,
            email=user_data.email,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    existing_registration = session.get(
        Registration,
        (user_data.username, event_id),
    )

    if existing_registration is not None:
        return existing_registration

    registration = Registration(
        username=user_data.username,
        event_id=event_id,
    )

    session.add(registration)
    session.commit()
    session.refresh(registration)

    return registration


@router.delete("")
def delete_all_events(session: SessionDep):
    """
    Elimina tutti gli eventi e tutte le registrazioni associate.
    """
    registrations = session.exec(select(Registration)).all()

    for registration in registrations:
        session.delete(registration)

    events = session.exec(select(Event)).all()

    for event in events:
        session.delete(event)

    session.commit()

    return {"message": "All events deleted"}


@router.delete("/{event_id}")
def delete_event(event_id: int, session: SessionDep):
    """
    Elimina un evento e tutte le registrazioni associate.
    """
    event = session.get(Event, event_id)

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    registrations = session.exec(
        select(Registration).where(Registration.event_id == event_id)
    ).all()

    for registration in registrations:
        session.delete(registration)

    session.delete(event)
    session.commit()

    return {"message": "Event deleted"}