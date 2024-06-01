from pydantic import BaseModel
from typing import Optional

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