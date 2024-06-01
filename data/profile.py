from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Entidad para definir los perfiles
class Profile(BaseModel):
   userid: str
   username: str
   gender: str
   looking_for: str
   age: int
   education: str
   ethnicity: str
   is_match_plus: bool
   latitud: float
   longitud: float
   last_like_date: datetime
   like_counter: int
   superlike_counter: int