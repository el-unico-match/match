from pydantic import BaseModel
from typing import Optional

# Entidad para definir los matchs
class Match(BaseModel):
   matchid: str
   userid_1: str
   qualification_1: str
   userid_2: str
   qualification_2: str