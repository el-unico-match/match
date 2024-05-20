from pydantic import BaseModel
from typing import Optional

# Entidades para definir los matchs
class MatchIn(BaseModel):
   userid_1: str
   qualification_1: str
   userid_2: str
   qualification_2: str
   
class Match(BaseModel):
   id: int
   userid_1: str
   qualification_1: str
   userid_2: str
   qualification_2: str