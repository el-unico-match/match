from pydantic import BaseModel
from typing import Optional

# Entidades para definir los matchs
class MatchIn(BaseModel):
   userid_qualificator: str
   userid_qualificated: str
   qualification:str

class UserOutModel(BaseModel):
   userid: str
   username: str
   qualification: str

class MatchOut(BaseModel):
   myself: UserOutModel
   matched: UserOutModel
   
class Match(BaseModel):
   id: int
   userid_qualificator: str
   userid_qualificated: str
   qualification:str