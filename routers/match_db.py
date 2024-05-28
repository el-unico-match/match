from fastapi import APIRouter,Path,Depends,Response,HTTPException
#from data.schemas.profile import Profile
#from data.models.profile import profiles as profiles_model
from data.match import Match,MatchIn,MatchOut
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
#    print(profile)
#    print(profile["userid"])
#    print(profile["username"])
    schema= {"userid":profile["userid"],
         	"username":profile["username"],
	        "email":profile["email"],
			"description":profile["description"],
			"gender":profile["gender"],
			"looking_for":profile["looking_for"],
			"age":int(profile["age"]),
			"education":profile["education"],
	        "ethnicity":profile["ethnicity"]
			}
#    print("schema:")
#    print(schema)
#    print(type(schema))
    return schema			

def profiles_schema(profiles)-> list:
   list=[]
   for profile in profiles:
       list.append(Profile(**profile_schema(profile)))
   return list			

def match_schema(match)-> dict:
#    print(profile)
#    print(profile["userid"])
#    print(profile["username"])
    schema= {"id":match["id"],
         	"userid_1":match["userid_1"],
	        "qualification_1":match["qualification_1"],
			"userid_2":match["userid_2"],
			"username_2":match["username_2"],
			"qualification_2":match["qualification_2"]
			}
#    print("schema:")
#    print(schema)
#    print(type(schema))
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
##    matchs=client.matchs
##    query = matchs.select().where(and_(matchs.columns.userid_1==id,matchs.columns.qualification_1 == "like",matchs.columns.qualification_2 == "like") )
#    query = matchs.select().where(matchs.columns.qualification_2 == "like")
    select_clause=' SELECT matchs.id,matchs.userid_1,matchs.qualification_1,matchs.userid_2,profiles.username as username_2,matchs.qualification_2'
    from_clause=' FROM profiles'
    join_clause=' FULL OUTER JOIN matchs ON matchs.userid_2 = profiles.userid'
    where_clause=' WHERE matchs.userid_1=:id AND matchs.qualification_1 = :qualification AND matchs.qualification_2 = :qualification'
    matchs_results = select_clause+from_clause+join_clause+where_clause
#    return await client_db.fetch_all(query)
    results=await client_db.fetch_all(query=matchs_results,values={"id":id,"qualification":"like"})
    for result in results:
	    print(tuple(result.values()))
    return matchs_schema(results)    
	
#@router.get("/user/{id}/matchs/filter",response_model=Profile,summary="Retorna un perfil que coincida con el filtro")
#@router.get("/user/{id}/matchs/filter",response_model=List[Profile],summary="Retorna un perfil que coincida con el filtro!!")
@router.get("/user/{id}/matchs/filter",response_model=Profile,summary="Retorna un perfil que coincida con el filtro!")
async def filter(id:str,gender:Union[str, None] = None,age:Union[int, None] = None,education:Union[str, None] = None,ethnicity:Union[str, None] = None,client_db = Depends(client.get_db)):
    return await filter_version_2(id,gender,age,education,ethnicity,client_db)

async def filter_version_1(id:str,gender:Union[str, None] = None,age:Union[int, None] = None,education:Union[str, None] = None,ethnicity:Union[str, None] = None,client_db = Depends(client.get_db)):
##    print("Implementar filtro")
#    return Profile(userid = "66304a6b2891cdcfebdbdc6f",
#   username = "Margot Robbie",
#   email = "mrobbie@hollywood.com",
#   description = "Actress",
#   gender = "Mujer",
#   looking_for = "Hombre",
#   age = 33,
#   education = "Estudios secundarios",
#   ethnicity = "") 	
##    query = client.profiles.filter(profiles.gender == gender, profiles.age==age,profiles.education==education,profiles.ethnicity==ethnicity)
##	return await client_db.fetch_all(query)


#probar esto
    arguments = {}
    select_clause='SELECT *'# profiles.userid,profiles.username ,profiles.email ,profiles.description,profiles.gender,profiles.looking_for,profiles.age,profiles.education,profiles.ethnicity'
    from_clause=' FROM profiles'
    join_clause=' FULL OUTER JOIN matchs ON profiles.userid = matchs.userid_2'# AND profiles.userid = matchs.userid_1'
    where_clause=''# WHERE matchs.userid_1=:id'# AND matchs.id IS NULL'	
    query_ = select_clause+from_clause+join_clause+where_clause
#    query_ = 'SELECT * FROM profiles JOIN matchs ON matchs.userid_2 = profiles.userid WHERE matchs.userid_1 = :id'
#    arguments['id']=id
    if ( gender != None):
        print("filtrar por genero") 
        query_  =query_  + ' AND profiles.gender = :gender'
        arguments['gender']=gender
    if ( age != None):
        print("filtrar por edad") 	
        query_  =query_  + ' AND profiles.age = :age'
        arguments['age']=age
    if ( education != None):
        print("filtrar por educacion") 	
        query_  =query_  + ' AND profiles.education = :education'
        arguments['education']=education
    if ( ethnicity != None):
        print("filtrar por etnia") 	
        query_  =query_  + ' AND profiles.ethnicity = :ethnicity'
        arguments['ethnicity']=ethnicity

    print(query_)
    print(arguments)
#    return await client_db.fetch_all(query=query_,values=arguments)	
#    return await client_db.fetch_all(query = 'SELECT * FROM profiles WHERE true',values={})
#    select_clause='SELECT profiles.userid,profiles.username ,profiles.email ,profiles.description,profiles.gender,profiles.looking_for,profiles.age,profiles.education,profiles.ethnicity'
#    from_clause=' FROM matchs'
#    join_clause=' FULL OUTER JOIN profiles ON profiles.userid = matchs.userid_2'
#    where_clause=' WHERE matchs.id IS NULL'	
#    query = select_clause+from_clause+join_clause+where_clause
#    print(query)
    results= await client_db.fetch_all(query=query_,values=arguments)
    for result in results:
	    print(tuple(result.values()))
    return ""

async def filter_version_2(id:str,gender:Union[str, None] = None,age:Union[int, None] = None,education:Union[str, None] = None,ethnicity:Union[str, None] = None,client_db = Depends(client.get_db)):

    arguments = {}
	#obtengo todos los perfiles que no son los de userid_1
    all_profiles='SELECT * FROM profiles WHERE profiles.userid <> :id'
	
	#obtengo los perfiles a los que el userid_1 le dio like o dislike (es decir cuya qualification_2 no es nula)
    select_clause=' SELECT profiles.userid,profiles.username ,profiles.email ,profiles.description,profiles.gender,profiles.looking_for,profiles.age,profiles.education,profiles.ethnicity'
    from_clause=' FROM profiles'
    join_clause=' FULL OUTER JOIN matchs ON matchs.userid_2 = profiles.userid'
    where_clause=' WHERE matchs.userid_1=:id AND matchs.qualification_2 IS NOT NULL'
    viewed_profiles = select_clause+from_clause+join_clause+where_clause

    arguments['id']=id
	
	#agrego los filtros que corresponda
    if ( gender != None):
        print("filtrar por genero") 
        all_profiles  =all_profiles  + ' AND profiles.gender = :gender'
        viewed_profiles  =viewed_profiles  + ' AND profiles.gender = :gender'
        arguments['gender']=gender
    if ( age != None):
        print("filtrar por edad") 	
        all_profiles  =all_profiles  + ' AND profiles.age = :age'
        viewed_profiles  =viewed_profiles  + ' AND profiles.age = :age'
        arguments['age']=age
    if ( education != None):
        print("filtrar por educacion") 	
        all_profiles  =all_profiles  + ' AND profiles.education = :education'
        viewed_profiles  =viewed_profiles  + ' AND profiles.education = :education'
        arguments['education']=education
    if ( ethnicity != None):
        print("filtrar por etnia") 	
        all_profiles  =all_profiles  + ' AND profiles.education = :education'
        viewed_profiles  =viewed_profiles  + ' AND profiles.education = :education'
        arguments['ethnicity']=ethnicity

    #me quedo solo con los perfiles que no ha visto todavía el usuario		
    query_=all_profiles+' EXCEPT'+viewed_profiles
		
    print(query_)
    print(arguments)

#    results= await client_db.fetch_all(query=query_,values=arguments)
#    for result in results:
#	    print(tuple(result.values()))
#    return ""	
    results = await client_db.fetch_one(query=query_,values=arguments) 
#    print({**results})
#    print(type({**results}))
#    print({results["userid"],results["username"]})
#    return Profile(**profile_schema(results))
    #TODO: revisar porque falla el return de los datos obtenidos por la query
    if(not results):
       raise HTTPException(status_code=404,detail="No se han encontrado personas para esta consulta")	    
    return profile_schema(results)  

@router.post("/user/{id}/match/preference",summary="Agrega un nuevo match")
async def define_preference(id:str,match:MatchIn,client_db = Depends(client.get_db)):
    await define_preference_version_2(id,match,client_db)

async def define_preference_version_1(id:str,
match:MatchIn,client_db = Depends(client.get_db)):
#async def define_preference(id:str,candidateid:str,qualification:str,client_db = Depends(client.get_db)):
#    print("Implementar funcionalidad de like y dislike")
#
# La tabla de match va a tener que tener siempre dos filas por cada operación:
# la calificación que dio el usuario 1 al usuario 2, y la calificación que recibio #el usuario 1 del usuario 2 (esto es porque sin estas dos filas va a resultar más #dificil poder filtrar perfiles en otras operaciones del microservicio)
# ejemplo:
# userid_1,qualification_1,userid_2,qualification_2
# 3,null,2,like
# 2,like,3,null

#    matchs=client.matchs
#    query_1=matchs.select().where(and_(matchs.columns.userid_1==match.userid_1,matchs.columns.userid_2==match.userid_2))
#    record_id_1 = await client_db.execute(query_1)
    record_id_1 = await find_match(client_db,match.userid_1,match.userid_2)
    print(record_id_1)
#    return record_id
    if(record_id_1):
#        query_2=update_preference(match.userid_1,match.qualification_1,match.userid_2,match.qualification_2)
        print("actualización 1 de match")  
        query_1=update_preference_1(record_id_1,match.userid_1,match.userid_2,match.qualification_2)
    else:
#        query_1=matchs.select().where(and_(matchs.columns.userid_2==match.userid_1,matchs.columns.userid_1==match.userid_2))
#        record_id_2 = await client_db.execute(query_1)
        record_id_2 = await find_match(client_db,match.userid_2,match.userid_1)
        print(record_id_2)
        if(record_id_2):
#            query_2=update_preference(match.userid_2,match.qualification_2,match.userid_1,match.qualification_1)
            print("actualización 2 de match") 
            query_1=update_preference_2(record_id_2,match.userid_1,match.userid_2,match.qualification_2)
        else:
#            query_2=insert_preference(match.userid_1,match.qualification_1,match.userid_2,match.qualification_2)
            print("inserción de nuevo de match") 
            query_1=insert_preference(match.userid_1,match.userid_2,match.qualification_2)



#	query_2 = insert.values(
##	matchid =match.matchid,
#	userid_1 =match.userid_1,
#    qualification_1 =match.qualification_1,
#    userid_2 =match.userid_2,
#    qualification_2 =match.qualification_2
#    )
##    print("query:"+str(query))

    last_record_id = await client_db.execute(query_1)
    return {**match.dict(),"matchid": last_record_id}

async def define_preference_version_2(id:str,
match:MatchIn,client_db = Depends(client.get_db)):	
	#buscar si en la tabla de match aparece el match asociado al usuario 1 y usuario 2
	#si aparece entonces: 
    #buscar el match asociado al usuario 2 y usuario 1
	#actualizar ambos registros
    #sino aparece entonces:
    #crear ambos registros	

    matchs=client.matchs	
	#busco si en la tabla de match aparece el match asociado al usuario 1 y usuario 2
    record_id_1 = await find_match(client_db,match.userid_1,match.userid_2)
    print(record_id_1)
    if(record_id_1):	
        #busco el match asociado al usuario 2 y usuario 1
        record_id_2 = await find_match(client_db,match.userid_2,match.userid_1)
        print(record_id_2)
        #actualizo ambos registros	
        print("actualización de match")  		
        query_1=matchs.update().where(matchs.columns.id == record_id_1).values(
    userid_1 =match.userid_1,
    userid_2 =match.userid_2,
    qualification_2 =match.qualification_2
    )
        query_2=matchs.update().where(matchs.columns.id == record_id_2).values(
    userid_1 =match.userid_2,
    userid_2 =match.userid_1,
    qualification_1 =match.qualification_2
    )
    else:
        #creo ambos registros
        print("inserción de nuevo de match")
        query_1=matchs.insert().values(
    userid_1 =match.userid_1,
    userid_2 =match.userid_2,
    qualification_2 =match.qualification_2
    )
        query_2=matchs.insert().values(
    userid_1 =match.userid_2,
    userid_2 =match.userid_1,
    qualification_1 =match.qualification_2
    )

    last_record_id_1 = await client_db.execute(query_1)
    last_record_id_2 = await client_db.execute(query_2)
#    print({"matchid": last_record_id_1,"userid_1":match.userid_1,"qualification_1":None,"userid_2":match.userid_2,"qualification_2":match.qualification_2})
#    print({"matchid": last_record_id_2,"userid_1":match.userid_2,"qualification_1":match.qualification_2,"userid_2":match.userid_1,"qualification_2":None})	
		
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