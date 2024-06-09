import math
import logging
import model.client as client
from settings import settings
from datetime import datetime
from typing import List,Union

from model.profile import Profile, Filter
from endpoints.getSwipes import get_swipes_list
from model.match import Match,MatchIn,MatchOut, SwipesOut
from fastapi import APIRouter,Path,Depends,Response,HTTPException

from data.match_data import MatchData
from data.filter_data import FilterData
from data.profile_data import ProfileData


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
            "qualification_date":match["qualification_date_1"],
        },
        "matched": {
            "userid":match["userid_2"],
            "username":match["username_2"],
            "qualification": match["qualification_2"],
            "qualification_date": match["qualification_date_2"],
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

@router.get(
        "/user/{id}/matchs",
        response_model=List[MatchOut],
        summary="Retorna una lista con todos los matchs")
async def view_matchs(id:str,client_db = Depends(client.get_db)):
    logger.error("retornando lista de matchs")
    matchdata = MatchData(client_db)

    return matchs_schema(results) 
	
@router.get("/user/{id}/profiles/set_filter", response_model=Profile,summary="Actualiza el filtro de candidator para el usuario.")
async def set_filter(filter: Filter, client_db = Depends(client.get_db)):
    filterdata = FilterData(client_db)
    await filterdata.update(filter)

@router.get("/user/{id}/profiles/nextcandidate",response_model=Profile,summary="Retorna un perfil que coincida con el filtro!")
async def next_candidate(id:str, client_db = Depends(client.get_db)):
    logger.error("retornando perfil que coincida con el filtro")
    profiledata = ProfileData(client_db)
    results = await profiledata.get_valid_candidates(id)
    
    if (myfilter.distance != None):
        filterdata = FilterData(client_db)
        myfilter = await filterdata.get_by_id(id)
        myprofile = await profiledata.get_by_id(id)

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
            if (dist < myfilter.distance * myfilter.distance):
                return profile_schema(row)
        return Response(status_code=204,content="No se han encontrado perfiles para esta consulta")
    
    if (results):
        return profile_schema(results[0])
    #TODO: revisar porque falla el return de los datos obtenidos por la query
    return Response(status_code=204,content="No se han encontrado perfiles para esta consulta")

#match/swipe
@router.post("/user/{id}/match/preference",summary="Agrega un nuevo match")
async def define_preference(id:str,match:MatchIn,client_db = Depends(client.get_db)):
    logger.error("agregando un nuevo match")
    matchdata = MatchData(client_db)
    profiledata = ProfileData(client_db)
    await profiledata.spend_likes(id, match.qualification)
    await matchdata.add_or_update(match)

@router.post("/user/match/profile",summary="Crea un nuevo perfil", response_model=Profile)
async def create_profile(new_profile:Profile,client_db = Depends(client.get_db)): 
    filterdata = FilterData(client_db)
    profiledata = ProfileData(client_db)

    await filterdata.new(new_profile.userid)

    logger.info("creando el perfil en base de datos")	
    try:
        await profiledata.new(new_profile)
        result = await profiledata.get_by_id(new_profile.userid)

        print(tuple(result.values()))
        return profile_schema(result)
    except Exception as e:
        print(e)
        logger.error(e)
        raise HTTPException(status_code=500,detail="ERROR: "+ str(e))

@router.put("/user/{id}/match/profile/",summary="Actualiza el perfil solicitado", response_model=Profile)
async def update_profile(updated_profile:Profile,client_db = Depends(client.get_db),id: str = Path(..., description="El id del usuario")):     
    profiledata = ProfileData(client_db)
    
    logger.info("actualizando el perfil en base de datos")
    try: 	
        await profiledata.update(updated_profile)
        result = await profiledata.get_by_id(updated_profile.userid)

        print(tuple(result.values()))
        return profile_schema(result)
    except Exception as e:
        print(e)
        logger.error(e)
        raise HTTPException(status_code=404,detail="No se ha encontrado el perfil") 		

@router.get("/user/{id}/match/profile/",summary="Obtiene el perfil solicitado", response_model=Profile)
async def view_profile(id: str = Path(..., description="El id del usuario"), client_db = Depends(client.get_db)):     
    profiledata = ProfileData(client_db)
    try:
        result = await profiledata.get_by_id(id)
        return profile_schema(result)
    except Exception as e:
        print(e)
        logger.error(e)
        raise HTTPException(status_code=404,detail="No se ha encontrado el perfil") 		

@router.post("/user/match/notification",summary="Notificar que se envio un mensaje", response_class=Response)
async def notification(userid_sender:str,userid_reciever:str,client_db = Depends(client.get_db))-> None:
    matchdata = MatchData(client_db)
    await matchdata.nofity_message(userid_sender,userid_reciever)
    return Response(status_code=200, content="Mensaje informado exitosamente")

@router.post("/user/match/block",summary="Bloquear un usuario", response_class=Response)
async def block_user(userid_bloquer:str,userid_blocked:str,client_db = Depends(client.get_db))-> None:
    matchdata = MatchData(client_db)
    await matchdata.block_user(userid_bloquer, userid_blocked)
    return Response(status_code=200, content="Usuario bloqueado exitosamente")

@router.get("/match/swipes",response_model=List[SwipesOut],summary="Retorna una lista con todos los matchs")
async def get_match_swipes(    
    swiper_id: Union[str, None] = None,
    swiper_names: Union[str,None] = None,
    superlikes: Union[bool, None] = None,
    matchs: Union[bool, None] = None,
    pending: Union[bool, None] = None,
    likes: Union[bool, None] = None,
    dislikes: Union[bool, None] = None,
    blocked: Union[bool, None] = None,
    client_db = Depends(client.get_db)
    ):
    return await get_swipes_list(swiper_id, swiper_names, superlikes, matchs, pending, likes, dislikes, blocked, client_db)