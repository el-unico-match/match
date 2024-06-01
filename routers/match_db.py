from fastapi import APIRouter,Path,Depends,Response,HTTPException
#from data.schemas.profile import Profile
#from data.models.profile import profiles as profiles_model
from data.match import Match,MatchIn,MatchOut
from data.profile import Profile
from typing import List,Union
from bson import ObjectId
from settings import Settings
from sqlalchemy import and_
import logging
import data.client as client

settings=Settings()

logging.basicConfig(filename=settings.log_filename,level=settings.logging_level)
logger=logging.getLogger(__name__)  
			
def profile_schema(profile)-> dict:
    schema= {"userid":profile["userid"],
         	"username":profile["username"],
			"gender":profile["gender"],
			"looking_for":profile["looking_for"],
			"age":int(profile["age"]),
			"education":profile["education"],
	        "ethnicity":profile["ethnicity"],
            "is_match_plus":profile["is_match_plus"]
			}
    return schema			

def profiles_schema(profiles)-> list:
   list=[]
   for profile in profiles:
       list.append(Profile(**profile_schema(profile)))
   return list			

def match_schema(match)-> dict:
    schema= {
        "myself": {
            "userid":match["userid_1"],
            "username":match["username_1"],
            "qualification":match["qualification_1"],
        },
        "matched": {
            "userid":match["userid_2"],
            "username":match["username_2"],
            "qualification":match["qualification_2"]
        }
    }
    return schema

def matchs_schema(matchs)-> list:
   list=[]
   for match in matchs:
       list.append(MatchOut(**match_schema(match)))
   return list	
	
router=APIRouter(tags=["match"])

# Operaciones de la API
@router.get("/status",summary="Retorna el estado del servicio")
async def view_status(): 
    logger.info("retornando status")
    return {"status":"ok"}

@router.get("/user/{id}/matchs",response_model=List[MatchOut]
,summary="Retorna una lista con todos los matchs")
async def view_matchs(id:str,client_db = Depends(client.get_db)):
    logger.error("retornando lista de matchs")

    sql_query = \
        'Select orig.userid_qualificator userid_1, orig.userid_qualificated userid_2,'\
        '       orig.qualification qualification_1, dest.qualification qualification_2,'\
        '       pf1.name username_1, pf2.name username_2'\
        'from matchs orig'\
        '   inner join profiles pf1 on orig.userid_qualificator = pf1.userid'\
        '   inner join matchs dest on orig.userid_qualificated = dest.userid_qualificator'\
        '   inner join profiles pf2 on orig.userid_qualificated = pf2.userid'\
        'where orig.qualification = :like'\
        '  and dest.qualification = :like'\
        '  and orig.userid_qualificator = :id'
    
    results=await client_db.fetch_all(query = sql_query, values = {"id":id,"like":"like"})
    for result in results:
	    print(tuple(result.values()))

    return matchs_schema(results) 
	
#@router.get("/user/{id}/matchs/filter",response_model=Profile,summary="Retorna un perfil que coincida con el filtro")
#@router.get("/user/{id}/matchs/filter",response_model=List[Profile],summary="Retorna un perfil que coincida con el filtro!!")
@router.get("/user/{id}/profiles/filter",response_model=Profile,summary="Retorna un perfil que coincida con el filtro!")
async def filter(
    id:str,
    gender:Union[str, None] = None,
    age_from:Union[int, None] = None,
    age_to:Union[int, None] = None,
    education:Union[str, None] = None,
    ethnicity:Union[str, None] = None,
    client_db = Depends(client.get_db)
):
    logger.error("retornando perfil que coincida con el filtro")
    query = "SELECT * FROM profiles WHERE profiles.userid = :id"
    result = await client_db.fetch_one(query = query, values={"id": id})
    print(result)
    if not result:
        raise HTTPException(status_code=404,detail="No se han encontrado perfiles con ese id")    
    
    arguments = { 'id': id }
    sql_query = \
        'Select pf.*'\
        'from profiles pf'\
        '   left join matchs m on m.userid_qualificator = :id and pf.userid = m.userid_qualificated'\
        'where pf.userid <> :id and m.id is null'\
        'order by pf.is_match_plus desc'
    
    if (gender != None):
        sql_query += ' and pf.gender = :gender'
        arguments["gender"] = gender
    
    if (age_from != None):
        sql_query += ' and pf.age >= :age_from'
        arguments["age_from"] = age_from
    
    if (age_to != None):
        sql_query += ' and pf.age <= :age_to'
        arguments["age_to"] = age_to
    
    if (education != None):
        sql_query += ' and pf.education = :education'
        arguments["education"] = education
    
    if (ethnicity != None):
        sql_query += ' and pf.ethnicity = :ethnicity'
        arguments["ethnicity"] = ethnicity
    
    
    results = await client_db.fetch_one(query = sql_query, values = arguments) 
    #TODO: revisar porque falla el return de los datos obtenidos por la query
    if(not results):
       raise HTTPException(status_code=404,detail="No se han encontrado perfiles para esta consulta")	    
    return profile_schema(results)  

#match/swipe
@router.post("/user/{id}/match/preference",summary="Agrega un nuevo match")
async def define_preference(id:str,match:MatchIn,client_db = Depends(client.get_db)):
    logger.error("agregando un nuevo match")
    
    client.matchs.insert().values(
        userid_qualificator = match.userid_qualificator,
        userid_qualificated = match.userid_qualificated,
        qualification = match.qualification
    )

#FALTA

def find_match(client_db,the_user_1,the_user_2):
    matchs=client.matchs
    query=matchs.select().where(and_(matchs.columns.userid_1==the_user_1,matchs.columns.userid_2==the_user_2))
#    record_id_1=await client_db.execute(query)    	
#    print("record_id:"+(record_id_1))
#    return record_id_1
    return client_db.execute(query)
	
def update_preference_1(the_matchid,the_userid_1,the_userid_2,the_qualification_2):
    matchs=client.matchs
    return matchs.update().where(matchs.columns.id == the_matchid).values(
#    id =the_matchid,
    userid_1 =the_userid_1,
#    qualification_1 =the_qualification_1,
    userid_2 =the_userid_2,
    qualification_2 =the_qualification_2
    )

def update_preference_2(the_matchid,the_userid_1,the_userid_2,the_qualification_2):
    matchs=client.matchs
    return matchs.update().where(matchs.columns.id == the_matchid).values(
#    id =the_matchid,
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
        gender =new_profile.gender,
        looking_for =new_profile.looking_for,
        age =new_profile.age,
        education =new_profile.education,
        ethnicity =new_profile.ethnicity,
        is_match_plus=False
	)
    logger.info("creando el perfil en base de datos")	
    try:
        await client_db.execute(query)
    except Exception as e:
#      logger.error(str(e))
        print(e)
        logger.error("el perfil ya existe")      				
        raise HTTPException(status_code=400,detail="El perfil ya existe")  		
#    print("Implementar funcionalidad de creación de perfil")
	  
@router.put("/user/{id}/match/profile/",summary="Actualiza el perfil solicitado", response_class=Response)
async def update_profile(updated_profile:Profile,client_db = Depends(client.get_db),id: str = Path(..., description="El id del usuario"))-> None:     
    profiles = client.profiles
    query = profiles.update().where(profiles.columns.userid ==updated_profile.userid).values(
        username = updated_profile.username,
        gender = updated_profile.gender,
        looking_for = updated_profile.looking_for,
        age = updated_profile.age,
        education = updated_profile.education,
        ethnicity = updated_profile.ethnicity,
        is_match_plus = updated_profile.is_match_plus
    )

    logger.info("actualizando el perfil en base de datos")
    try: 	
        await client_db.execute(query)
        ##query_result = "SELECT * FROM profiles WHERE userid = :id"		
        #query_result=profiles.select().where(profiles.columns.userid ==updated_profile.userid)
        #result=await client_db.fetch_one(query=query_result)
        #print (result)
        #return profile_schema(result)  		
    except Exception as e:
#      logger.error(str(e))
        print(e)
        logger.error("no se ha encontrado el perfil")      		
        raise HTTPException(status_code=404,detail="No se ha encontrado el perfil") 		
#    print("Implementar funcionalidad de actualización de perfil")
    
