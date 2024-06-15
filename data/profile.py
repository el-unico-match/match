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
   like_counter: int
   superlike_counter: int

class Filter(BaseException):
   userid: str
   gender: str
   age_from: int
   age_to: int
   education: str
   ethnicity: str
   distance: float