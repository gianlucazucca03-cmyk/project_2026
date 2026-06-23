from pydantic import StrictStr
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    """
    Modello Utente
    """
    
    username: StrictStr = Field(primary_key=True)
    name: StrictStr
    email: StrictStr
    
