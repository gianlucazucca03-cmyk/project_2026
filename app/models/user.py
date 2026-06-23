from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    """
    Modello Utente/giocatore del sito di tornei di poker
    """
    
    username: str = Field(primary_key=True)
    name: str
    email: str
   
    