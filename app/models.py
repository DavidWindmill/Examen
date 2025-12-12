from datetime import datetime
from typing import List, Optional
from beanie import Document, PydanticObjectId
from pydantic import BaseModel

class FiltrosEvento(BaseModel):
    titulo: Optional[str] = None
    organizador: Optional[str] = None
    calendarios: Optional[List[str]] = None
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None