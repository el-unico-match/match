from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Union

# Entidades para definir los matchs
class MatchIn(BaseModel):
   userid_qualificator: str
   userid_qualificated: str
   qualification:str

class UserOutModel(BaseModel):
   userid: str
   username: str
   qualification: str
   qualification_date: datetime

class MatchOut(BaseModel):
   myself: UserOutModel
   matched: UserOutModel
   
class Match(BaseModel):
   id: int
   userid_qualificator: str
   userid_qualificated: str
   qualification:str

class SwipesOut(BaseModel):
   is_match: bool
   qualificator_id: str
   qualificator_name: str
   qualificator_swipe: str
   qualificator_date: str
   qualificator_blocked: bool
   qualificated_id: str
   qualificated_name: str
   qualificated_swipe: str 
   qualificated_date: str
   qualificated_blocked: bool

class MatchFilter(BaseModel):
   userid: str
   gender: Optional[str] = None
   age_from: Optional[int] = None
   age_to: Optional[int] = None
   education: Optional[str] = None
   ethnicity: Optional[str] = None
   distance: Optional[float] = None