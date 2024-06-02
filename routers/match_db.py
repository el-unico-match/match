from fastapi import APIRouter,Path,Depends,Response,HTTPException
from data.match import Match,MatchIn,MatchOut
from data.profile import Profile
from typing import List,Union
from settings import Settings
from datetime import datetime
import data.client as client
import logging
import math

settings=Settings()

logging.basicConfig(filename=settings.log_filename,level=settings.logging_level)
logger=logging.getLogger(__name__)  
			
def profile_schema(profile)-> dict:
    schema= {
        "userid":profile["userid"],
        "username":profile["username"],
        "gender":profile["gender"],
        "looking_for":profile["looking_for"],
        "age":int(profile["age"]),
        "education":profile["education"],
        "ethnicity":profile["ethnicity"],
        "is_match_plus":profile["is_match_plus"],
        "latitud":profile["latitud"],
        "longitud":profile["longitud"],
        "last_like_date":profile["last_like_date"],
        "like_counter":profile["like_counter"],
        "superlike_counter":profile["superlike_counter"],
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
        ' Select orig.userid_qualificator userid_1, orig.userid_qualificated userid_2,'\
        '        orig.qualification qualification_1, dest.qualification qualification_2,'\
        '        pf1.username username_1, pf2.username username_2'\
        ' from matchs orig'\
        '    inner join profiles pf1 on orig.userid_qualificator = pf1.userid'\
        '    inner join matchs dest on orig.userid_qualificated = dest.userid_qualificator and orig.userid_qualificator = dest.userid_qualificated'\
        '    inner join profiles pf2 on orig.userid_qualificated = pf2.userid'\
        ' where orig.qualification = :like'\
        '   and dest.qualification = :like'\
        '   and orig.userid_qualificator = :id'\
        '   and not orig.bloqued and not dest.blocked'\
        ' order by orig.last_message_date desc'
    
    results=await client_db.fetch_all(query = sql_query, values = {"id":id,"like":"like"})
    for result in results:
	    print(tuple(result.values()))

    return matchs_schema(results) 
	
@router.get("/user/{id}/profiles/filter",response_model=Profile,summary="Retorna un perfil que coincida con el filtro!")
async def filter(
    id:str,
    gender:Union[str, None] = None,
    age_from:Union[int, None] = None,
    age_to:Union[int, None] = None,
    education:Union[str, None] = None,
    ethnicity:Union[str, None] = None,
    distance:Union[float, None] = None,
    client_db = Depends(client.get_db)
):
    logger.error("retornando perfil que coincida con el filtro")
    query = "SELECT * FROM profiles WHERE profiles.userid = :id"
    myprofile = await client_db.fetch_one(query = query, values={"id": id})
    print(myprofile)
    if not myprofile:
        raise HTTPException(status_code=404,detail="No se han encontrado perfiles con ese id")    
    
    arguments = { 'id': id, "superlike":"superlike" }
    sql_query = \
        'Select pf.* '\
        'from profiles pf '\
        '   left join matchs m on m.userid_qualificator = :id and pf.userid = m.userid_qualificated '\
        '   left join matchs m2 on '\
        '                    m2.userid_qualificated = :id '\
        '                    and pf.userid = m2.userid_qualificator '\
        '                    and m2.qualification = :superlike '\
        'where pf.userid <> :id and m.id is null '
        
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

    sql_query += ' order by m2.userid_qualificator desc, pf.is_match_plus desc, pf.userid '
	
    results = await client_db.fetch_all(query = sql_query, values = arguments)

    if (distance != None):
        for row in results:
            # Para mejorar presicion usar cuentas correctas
            #rad = 6371000.0 # valor en metros
            #rad = 63710.0   # valor en cuadras
            rad = 6371.0    # valor en kilometros

            lat1 = math.radians(row["latitud"])
            lon1 = math.radians(row["longitud"])
            lat2 = math.radians(myprofile["latitud"])
            lon2 = math.radians(myprofile["longitud"])

            pos_row = [
                math.sin(lat1)*math.cos(lon1),
                math.sin(lat1)*math.sin(lon1),
                math.cos(lat1)
            ]
            pos_prof = [
                math.sin(lat2)*math.cos(lon2),
                math.sin(lat2)*math.sin(lon2),
                math.cos(lat2)
            ]

            xdist = pos_row[0]-pos_prof[0]
            ydist = pos_row[1]-pos_prof[1]
            zdist = pos_row[2]-pos_prof[2]

            # Distance squared
            dist = rad*rad*(xdist*xdist + ydist*ydist + zdist*zdist)
            if (dist < distance * distance):
                return profile_schema(row)
        raise HTTPException(status_code=200,detail="No se han encontrado perfiles para esta consulta")
    
    if (results):
        return profile_schema(results[0])
    #TODO: revisar porque falla el return de los datos obtenidos por la query
    raise HTTPException(status_code=200,detail="No se han encontrado perfiles para esta consulta")

#match/swipe
@router.post("/user/{id}/match/preference",summary="Agrega un nuevo match")
async def define_preference(id:str,match:MatchIn,client_db = Depends(client.get_db)):
    logger.error("agregando un nuevo match")
    
    query = "SELECT * FROM profiles WHERE profiles.userid = :id"
    myprofile = await client_db.fetch_one(query = query, values={"id": id})
    
    if (not myprofile['is_match_plus']):
        if (myprofile['last_like_date'].date() < datetime.now().date()):
            myprofile['like_counter'] = 0

        if (myprofile['like_counter'] > settings.LIKE_LIMITS):
            raise HTTPException(status_code=400,detail="Se alcanzo el limite de likes")
        
        if (match.qualification == 'like'):
            myprofile['last_like_date'] = datetime.now()
            myprofile['like_counter'] += 1
    else:
        if (myprofile['last_like_date'].date() < datetime.now().date()):
            myprofile['superlike_counter'] = 0
        
        if (myprofile['superlike_counter'] > settings.SUPERLIKE_LIMITS):
            raise HTTPException(status_code=400,detail="Se alcanzo el limite de superlikes")
        
        if (match.qualification == 'superlike'):
            myprofile['last_like_date'] = datetime.now()
            myprofile['superlike_counter'] += 1

    profiles = client.profiles
    query = profiles.update().where(profiles.columns.userid == id).values(myprofile)
    await client_db.execute(query)

    matchs = client.matchs
    # Por las dudas pero no deberia pasar
    # porque solo se muestran par hacer match los que no fueron calificados
    old_del = matchs.delete().where(
        matchs.columns.userid_qualificator == match.userid_qualificator,
        matchs.columns.userid_qualificated == match.userid_qualificated
    )
    await client_db.execute(old_del)

    new_match=client.matchs.insert().values(
        userid_qualificator = match.userid_qualificator,
        userid_qualificated = match.userid_qualificated,
        qualification = match.qualification
    )

    await client_db.execute(new_match)

@router.post("/user/match/profile",summary="Crea un nuevo perfil", response_class=Response)
async def create_profile(new_profile:Profile,client_db = Depends(client.get_db))-> None: 
    query = client.profiles.insert().values(userid =new_profile.userid,
        username          = new_profile.username,
        gender            = new_profile.gender,
        looking_for       = new_profile.looking_for,
        age               = new_profile.age,
        education         = new_profile.education,
        ethnicity         = new_profile.ethnicity,
        is_match_plus     = False,
        latitud           = new_profile.latitud,
        longitud          = new_profile.longitud,
        last_like_date    = datetime.now(),
        like_counter      = new_profile.like_counter,
        superlike_counter = new_profile.superlike_counter
	)
    logger.info("creando el perfil en base de datos")	
    try:
        await client_db.execute(query)
    except Exception as e:
        print(e)
        logger.error(e)
        raise HTTPException(status_code=400,detail="El perfil ya existe")
	  
@router.put("/user/{id}/match/profile/",summary="Actualiza el perfil solicitado", response_class=Response)
async def update_profile(updated_profile:Profile,client_db = Depends(client.get_db),id: str = Path(..., description="El id del usuario"))-> None:     
    profiles = client.profiles
    query = profiles.update().where(profiles.columns.userid ==updated_profile.userid).values(
        username          = updated_profile.username,
        gender            = updated_profile.gender,
        looking_for       = updated_profile.looking_for,
        age               = updated_profile.age,
        education         = updated_profile.education,
        ethnicity         = updated_profile.ethnicity,
        is_match_plus     = updated_profile.is_match_plus,
        latitud           = updated_profile.latitud,
        longitud          = updated_profile.longitud,
        like_counter      = updated_profile.like_counter,
        superlike_counter = updated_profile.superlike_counter
    )

    logger.info("actualizando el perfil en base de datos")
    try: 	
        await client_db.execute(query)		
    except Exception as e:
        print(e)
        logger.error(e)
        raise HTTPException(status_code=404,detail="No se ha encontrado el perfil") 		
    
@router.post("/user/match/notification",summary="Notificar que se envio un mensaje", response_class=Response)
async def notification(userid_sender:str,userid_reciever:str,client_db = Depends(client.get_db))-> None:
    sql_query = \
        ' update matchs '\
        ' set last_message_date = NOW() '\
        ' where m.userid_qualificator = :sender and m.userid_qualificated = :reciever or '\
        '       m.userid_qualificator = :reciever and m.userid_qualificated = :sender '

    await client_db.execute(query = sql_query, values = { 
        "sender": userid_sender,
        "reciever": userid_reciever
    })

@router.post("/user/match/block",summary="Bloquear un usuario", response_class=Response)
async def block_user(userid_bloquer:str,userid_blocked:str,client_db = Depends(client.get_db))-> None:
    sql_query = \
        ' update matchs '\
        ' set blocked = TRUE '\
        ' where m.userid_qualificator = :blocker and m.userid_qualificated = :blocked '

    await client_db.execute(query = sql_query, values = { 
        "blocker": userid_bloquer,
        "blocked": userid_blocked
    })
