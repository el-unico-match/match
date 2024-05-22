from fastapi import APIRouter,Path,Depends,Response,HTTPException
#from data.schemas.profile import Profile
#from data.models.profile import profiles as profiles_model
from data.match import Match,MatchIn
from data.profile import Profile
from typing import List,Union
from bson import ObjectId
from settings import Settings
from sqlalchemy import and_
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

@router.get("/user/{id}/matchs",response_model=List[Match],summary="Retorna una lista con todos los matchs")
async def view_matchs(id:str,client_db = Depends(client.get_db)):
#    print("Implementar lista de matchs")
#   matchs=[]
#   matchs.append(
#   Match(matchid = "66304a6b2891cdcfebdbdc6f",
#   userid_1 = "1",
#   qualification_1 = "like",
#   userid_2 = "2",
#   qualification_2 = "like"))
#   return matchs
#    query = client.matchs.filter(matchs.userid_1==id,matchs.qualification_1 == "like",matchs.qualification_2 == "like")
    matchs=client.matchs
    query = matchs.select().where(and_(matchs.columns.userid_1==id,matchs.columns.qualification_1 == "like",matchs.columns.qualification_2 == "like") )
#    query = matchs.select().where(matchs.columns.qualification_2 == "like")
    return await client_db.fetch_all(query)
	
@router.get("/user/{id}/matchs/filter",response_model=Profile,summary="Retorna un perfil que coincida con el filtro")
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
#    query = client.profiles.filter(profiles.gender == gender, profiles.age==age,profiles.education==education,profiles.ethnicity==ethnicity)
#	return await client_db.fetch_all(query)
	
@router.post("/user/{id}/match/preference",summary="Agrega un nuevo match")
async def define_preference(id:str,
match:MatchIn,client_db = Depends(client.get_db)):
#async def define_preference(id:str,candidateid:str,qualification:str,client_db = Depends(client.get_db)):
#    print("Implementar funcionalidad de like y dislike")
    matchs=client.matchs
    query_1=matchs.select().where(and_(matchs.columns.userid_1==match.userid_1,matchs.columns.userid_2==match.userid_2))
    record_id_1 = await client_db.execute(query_1)
    print(record_id_1)
#    return record_id
    if(record_id_1):
#        query_2=update_preference(match.userid_1,match.qualification_1,match.userid_2,match.qualification_2)
        print("actualización 1 de match")  
        query_2=update_preference_1(match.userid_1,match.userid_2,match.qualification_2)
    else:
        query_1=matchs.select().where(and_(matchs.columns.userid_2==match.userid_1,matchs.columns.userid_1==match.userid_2))
        record_id_2 = await client_db.execute(query_1)
        print(record_id_2)
        if(record_id_2):
#            query_2=update_preference(match.userid_2,match.qualification_2,match.userid_1,match.qualification_1)
            print("actualización 2 de match") 
            query_2=update_preference_2(match.userid_1,match.userid_2,match.qualification_2)
        else:
#            query_2=insert_preference(match.userid_1,match.qualification_1,match.userid_2,match.qualification_2)
            print("inserción de nuevo de match") 
            query_2=insert_preference(match.userid_1,match.userid_2,match.qualification_2)



#	query_2 = insert.values(
##	matchid =match.matchid,
#	userid_1 =match.userid_1,
#    qualification_1 =match.qualification_1,
#    userid_2 =match.userid_2,
#    qualification_2 =match.qualification_2
#    )
##    print("query:"+str(query))

    last_record_id = await client_db.execute(query_2)
    return {**match.dict(),"matchid": last_record_id}

def update_preference_1(the_userid_1,the_userid_2,the_qualification_2):
	return client.matchs.update().values(
#	matchid =match.matchid,
	userid_1 =the_userid_1,
#    qualification_1 =the_qualification_1,
    userid_2 =the_userid_2,
    qualification_2 =the_qualification_2
    )

def update_preference_2(the_userid_1,the_userid_2,the_qualification_2):
	return client.matchs.update().values(
#	matchid =match.matchid,
	userid_1 =the_userid_2,
    qualification_1 =the_qualification_2,
    userid_2 =the_userid_1,
#    qualification_2 =the_qualification_2
    )	

def insert_preference(the_userid_1,the_userid_2,the_qualification_2):
	return client.matchs.insert().values(
#	matchid =match.matchid,
	userid_1 =the_userid_1,
#    qualification_1 =the_qualification_1,
    userid_2 =the_userid_2,
    qualification_2 =the_qualification_2
    )
	
@router.post("/user/match/profile",summary="Crea un nuevo perfil", response_class=Response)
async def create_profile(new_profile:Profile,client_db = Depends(client.get_db))-> None: 
    query = client.profiles.insert().values(userid =new_profile.userid,
	username =new_profile.username,
	email =new_profile.email,
	description =new_profile.description,
	gender =new_profile.gender,
	looking_for =new_profile.looking_for,
	age =new_profile.age,
	education =new_profile.education,
	ethnicity =new_profile.ethnicity
	)
    await client_db.execute(query)
#    print("Implementar funcionalidad de creación de perfil")
	  
@router.put("/user/{id}/match/profile/",summary="Actualiza el perfil solicitado", response_class=Response)
async def update_profile(updated_profile:Profile,client_db = Depends(client.get_db),id: str = Path(..., description="El id del usuario"))-> None:     
    query = client.profiles.update().values(userid =updated_profile.userid,
	username =updated_profile.username,
	email =updated_profile.email,
	description =updated_profile.description,
	gender =updated_profile.gender,
	looking_for =updated_profile.looking_for,
	age =updated_profile.age,
	education =updated_profile.education,
	ethnicity =updated_profile.ethnicity
	)
    await client_db.execute(query)
#    print("Implementar funcionalidad de actualización de perfil")