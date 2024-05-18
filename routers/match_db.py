from fastapi import APIRouter,Path,Depends,Response,HTTPException
from data.profile import Profile
from data.match import Match
from typing import List,Union
from bson import ObjectId
from settings import Settings
#import logging
import data.client as client

settings=Settings()

#logging.basicConfig(filename=settings.log_filename,level=settings.logging_level)
#logger=logging.getLogger(__name__)  
			
def profile_schema(profile)-> dict:
    return {"userid":profile["userid"],
         	"username":profile["username"],
	        "email":profile["email"],
			"description":profile["description"],
			"gender":profile["gender"],
			"looking_for":profile["looking_for"],
			"age":profile["age"],
			"education":profile["education"],
	        "ethnicity":profile["ethnicity"]
			}

def profiles_schema(profiles)-> list:
   list=[]
   for profile in profiles:
       list.append(Profile(**profile_schema(profile)))
   return list			
			
router=APIRouter(tags=["match"])


# Operaciones de la API

@router.get("/status",summary="Retorna el estado del servicio")
async def view_status(): 
    logger.info("retornando status")
    return {"status":"ok"}

@router.get("/user/{id}/matchs")
async def view_matchs(id:str,client_db = Depends(client.get_db)):
#    print("Implementar lista de matchs")
   matchs=[]
   matchs.append(
   Match(matchid = "66304a6b2891cdcfebdbdc6f",
   userid_1 = "1",
   qualification_1 = "like",
   userid_2 = "2",
   qualification_2 = "like"))
   return matchs
   
	
@router.get("/user/{id}/matchs/filter")
async def filter(id:str,gender:Union[str, None] = None,age:Union[int, None] = None,education:Union[str, None] = None,ethnicity:Union[str, None] = None,client_db = Depends(client.get_db)):
#    print("Implementar filtro")
    return Profile(userid = "66304a6b2891cdcfebdbdc6f",
   username = "Margot Robbie",
   email = "mrobbie@hollywood.com",
   description = "Actress",
   gender = "Mujer",
   looking_for = "Hombre",
   age = 33,
   education = "Estudios secundarios",
   ethnicity = "") 	
	
@router.get("/user/{id}/match/preference")
async def define_preference(id:str,candidateid=str,client_db = Depends(client.get_db)):
    print("Implementar funcionalidad de like y dislike")