from fastapi import APIRouter,Path,Depends,Response,HTTPException
from data.match import Match,MatchIn,MatchOut, SwipesOut, MatchFilter
from data.profile import Profile
from typing import List,Union
from endpoints.getSwipes import get_swipes_list
from endpoints.putBlock import update_block_state, PutBlockRequest
from endpoints.putWhitelist import update_whitelist, PutWhiteList
from settings import settings
from datetime import datetime
import data.client as client
import logging
import math

import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

if settings.mode=='production':
    server_key = settings.notification_server_key
    firebase_cred = credentials.Certificate(server_key)
    firebase_app = firebase_admin.initialize_app(firebase_cred)

#logging.basicConfig(format='%(asctime)s [%(filename)s] %(levelname)s %(message)s',filename=settings.log_filename,level=settings.logging_level)
logger=logging.getLogger(__name__)#settings.logger_name)
streamHandler = logging.StreamHandler()
streamHandler.setLevel(settings.logging_level)
formatter = logging.Formatter('%(levelname)s %(asctime)s [%(filename)s] %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

			
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
	
def filter_schema(filter)-> dict:
    schema = {
        "userid": filter["userid"],
        "gender": filter["gender"],
        "age_from": filter["age_from"],
        "age_to": filter["age_to"],
        "education": filter["education"],
        "ethnicity": filter["ethnicity"],
        "distance": filter["distance"]
    }
    return schema

router=APIRouter(tags=["match"])	
	
@router.post("/user/match/push_notification",summary="Envía una notificación a al destinatario correspondiente", response_class=Response)			
async def send_push_notification(destinationid:str,title:str, message:str, match:str,type:str)->None:	
    data = {
    'Match': match,
    'Tipo': type
    }
    send_push_notification(destinationid,title, message, data)
#    send_push_notification(destinationid,title, message)

	
def send_push_notification(destinationid,title, message, data=None):
    if settings.mode=='production':
        message = messaging.Message(
                  notification=messaging.Notification(
                  title=title,
                  body=message
                  ),
                  topic=destinationid
                  )
        if data:
            message.data = data

        response = messaging.send(message)

        logger.info("Se ha enviado exitosamente la notificación:"+response+" a:"+destinationid)	
	
#def send_push_notification(server_key, device_tokens, title, body, data=None):
#    cred = credentials.Certificate(server_key)
#    firebase_admin.initialize_app(cred)
#
#    message = messaging.MulticastMessage(
#        notification=messaging.Notification(
#            title=title,
#            body=body
#        ),
#        tokens=device_tokens
#    )
#    if data:
#        message.data = data
#
#    response = messaging.send_multicast(message)
#
#    logger.info("Se ha enviado exitosamente la notificación:"+response)

# Operaciones de la API
@router.get("/status",summary="Retorna el estado del servicio")
async def view_status(): 
    logger.info("retornando status")
    return {
        "status":"ok",
        "apikey_status": settings.apikey_status,
        "apikeys_count": len(settings.apikey_whitelist),
    }

@router.get("/log",summary="Retorna el log del servicio")
async def view_log (): 
   logger.info("retornando log")
   with open(settings.log_filename, "r") as file:
      contents = file.read()
      return contents

@router.get(
        "/user/{id}/matchs",
        response_model=List[MatchOut],
        summary="Retorna una lista con todos los matchs")
async def view_matchs(id:str,client_db = Depends(client.get_db)):
    logger.info("retornando lista de matchs")

    sql_query = '''
        Select orig.userid_qualificator userid_1, orig.userid_qualificated userid_2,
               orig.qualification qualification_1, dest.qualification qualification_2,
               orig.qualification_date qualification_date_1, dest.qualification_date qualification_date_2,
               pf1.username username_1, pf2.username username_2
        from matchs orig
           inner join profiles pf1 on orig.userid_qualificator = pf1.userid
           inner join matchs dest on orig.userid_qualificated = dest.userid_qualificator 
                                 and orig.userid_qualificator = dest.userid_qualificated
           inner join profiles pf2 on orig.userid_qualificated = pf2.userid
        where orig.qualification = :like
          and dest.qualification = :like
          and orig.userid_qualificator = :id
          and not orig.blocked and not dest.blocked
        order by orig.last_message_date desc
    '''
    
    results=await client_db.fetch_all(query = sql_query, values = {"id":id,"like":"like"})
    
    #for result in results:
    #    print(tuple(result.values()))
	
    matchs=matchs_schema(results) 
    logger.info(matchs)	
    return matchs	


@router.get(
        "/user/{id}/likes",
        response_model=List[MatchOut],
        summary="Retorna una lista con todos los likes")
async def view_likes(id:str,client_db = Depends(client.get_db)):
    logger.info("retornando lista de likes")

    sql_query = '''
        Select orig.userid_qualificator userid_1, orig.userid_qualificated userid_2,
               orig.qualification qualification_1, '' qualification_2,
               orig.qualification_date qualification_date_1, orig.qualification_date qualification_date_2,
               pf1.username username_1, pf2.username username_2
        from matchs orig
           inner join profiles pf1 on orig.userid_qualificator = pf1.userid
           left  join matchs dest on orig.userid_qualificated = dest.userid_qualificator 
                                 and orig.userid_qualificator = dest.userid_qualificated
			inner join profiles pf2 on orig.userid_qualificated = pf2.userid
        where orig.qualification in (:like, :superlike)
          and dest.userid_qualificated is NULL
          and orig.userid_qualificated = :id
          and not orig.blocked
        order by orig.last_message_date desc
    '''
    
    results=await client_db.fetch_all(query = sql_query, values = {"id":id,"like":"like", "superlike":"superlike"})
    
    #for result in results:
    #    print(tuple(result.values()))

    #return matchs_schema(results)
	
    likes=matchs_schema(results) 
    logger.info(likes)	
    return likes		
	
@router.get("/user/{id}/profiles/filter",response_model=Profile,summary="Retorna un perfil que coincida con el filtro!")
async def profiles_filter(
    id:str,
    gender:Union[str, None] = None,
    age_from:Union[int, None] = None,
    age_to:Union[int, None] = None,
    education:Union[str, None] = None,
    ethnicity:Union[str, None] = None,
    distance:Union[float, None] = None,
    client_db = Depends(client.get_db)
):
    logger.info("retornando perfil que coincida con el filtro")
    query = "SELECT * FROM profiles WHERE profiles.userid = :id"
    myprofile = await client_db.fetch_one(query = query, values={"id": id})
    print(myprofile)
    if not myprofile:
        logger.error("No se han encontrado perfiles con ese id")	
        raise HTTPException(status_code=404,detail="No se han encontrado perfiles con ese id")    
    
    arguments = { 'id': id, "superlike":"superlike" }
    sql_query = '''
        Select pf.*
        from profiles pf
           left join matchs m on m.userid_qualificator = :id and pf.userid = m.userid_qualificated
           left join matchs m2 on
                            m2.userid_qualificated = :id
                            and pf.userid = m2.userid_qualificator
                            and m2.qualification = :superlike
        where pf.userid <> :id and m.id is null
    '''
        
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

    sql_query += ' order by m2.userid_qualificator desc, pf.is_match_plus desc, pf.userid'
	
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
                profile=profile_schema(row)
                logger.info(profile)	
                return profile
        logger.info("No se han encontrado perfiles para esta consulta")				
        return Response(status_code=204,content="No se han encontrado perfiles para esta consulta")
    
    if (results):
        profile=profile_schema(results[0])
        logger.info(profile)
        return profile	
    logger.info("No se han encontrado perfiles para esta consulta")				
    return Response(status_code=204,content="No se han encontrado perfiles para esta consulta")

@router.get("/user/{id}/rewind",response_model=Profile,summary="Retorna el ultimo perfil que se le aplico preferencias!")
async def rewind(
    id:str,
    client_db = Depends(client.get_db)
):
    logger.info("retornando ultimo perfil que se le aplicion preferencia")
    query = "SELECT * FROM profiles WHERE profiles.userid = :id and is_match_plus"
    myprofile = await client_db.fetch_one(query = query, values={"id": id})
    print(myprofile)
    if not myprofile:
        logger.error("No se han encontrado perfiles con ese id que sea match plus")	
        raise HTTPException(status_code=404,detail="No se han encontrado perfiles con ese id que sea match plus")    
    
    arguments = { 'id': id }
    sql_query = '''
        SELECT pf.*
            FROM public.matchs as m
            Inner Join profiles pf on m.userid_qualificated = pf.userid
        WHERE userid_qualificator = :id
        order by m.id desc
    '''
	
    results = await client_db.fetch_all(query = sql_query, values = arguments)
    
    if (results):
        profile=profile_schema(results[0])
        logger.info(profile)
        return profile	
    logger.info("No se han encontrado perfiles para esta consulta")				
    return Response(status_code=204,content="No se han encontrado perfiles para esta consulta")

#match/swipe
@router.post("/user/{id}/match/preference",summary="Agrega un nuevo match")
async def define_preference(id:str,match:MatchIn,client_db = Depends(client.get_db)):
    logger.info("agregando un nuevo match")
    
    query = "SELECT * FROM profiles WHERE profiles.userid = :id"
    myprofile = await client_db.fetch_one(query = query, values={"id": id})
    newvalues = {
        "id": id,
        "last_like_date": myprofile["last_like_date"],
        "like_counter": myprofile["like_counter"],
        "superlike_counter": myprofile["superlike_counter"],
    }

    if (not myprofile['is_match_plus']):	
        if (match.qualification == 'superlike'):
            raise HTTPException(status_code=400,detail="Usuario normal no puede dar superlikes")

        if (myprofile['last_like_date'].date() < datetime.now().date()):
            newvalues['like_counter'] = 0

        if (match.qualification == 'like' and newvalues['like_counter'] > settings.LIKE_LIMITS):
            raise HTTPException(status_code=400,detail="Se alcanzo el limite de likes")
        
        if (match.qualification == 'like'):
            newvalues['last_like_date'] = datetime.now()
            newvalues['like_counter'] += 1
            body = 'Alguien te dio like'
            send_push_notification(match.userid_qualificated,'Nuevo like', body,{'Match': match.userid_qualificator,'Tipo': "Like"})
            if await receive_like_or_superlike(match.userid_qualificated,match.userid_qualificator,client_db):
                send_match_notification(match.userid_qualificator,match.userid_qualificated)               						
    else:
        if (myprofile['last_like_date'].date() < datetime.now().date()):
            newvalues['superlike_counter'] = 0
        
        if (match.qualification == 'superlike' and newvalues['superlike_counter'] > settings.SUPERLIKE_LIMITS):
            raise HTTPException(status_code=400,detail="Se alcanzo el limite de superlikes")
        
        if (match.qualification == 'superlike'):
            newvalues['last_like_date'] = datetime.now()
            newvalues['superlike_counter'] += 1
            body = myprofile['username']+' te dio superlike'	
            send_push_notification(match.userid_qualificated,'Nuevo superlike', body,{'Match': match.userid_qualificator,'Tipo': "SuperLike"})
            #...
            if await receive_like_or_superlike(match.userid_qualificated,match.userid_qualificator,client_db):
                send_match_notification(match.userid_qualificator,match.userid_qualificated) 			
			
        if (match.qualification == 'like'):
            body = myprofile['username']+' te dio like'	
            send_push_notification(match.userid_qualificated,'Nuevo like', body,{'Match': match.userid_qualificator,'Tipo': "Like"})			
            if await receive_like_or_superlike(match.userid_qualificated,match.userid_qualificator,client_db):
                send_match_notification(match.userid_qualificator,match.userid_qualificated) 			

    if (match.qualification == 'dislike'):
        if await receive_like_or_superlike(match.userid_qualificated,match.userid_qualificator,client_db):
            body = 'Perdiste la posibilidad de hacer match'			
            send_push_notification(match.userid_qualificator,'Nuevo match perdido', body,{'Match': match.userid_qualificated,'Tipo': "MatchPerdido"})	
				
    query = '''
        update profiles 
        set last_like_date = :last_like_date,
            superlike_counter = :superlike_counter,
            like_counter = :like_counter
        where userid = :id
    '''

    await client_db.execute(query = query, values = newvalues)

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
        qualification = match.qualification,
        blocked = False,
        qualification_date = datetime.now(),
    )

    await client_db.execute(new_match)

async def receive_like_or_superlike(calificated,calificator,client_db):
    query = "SELECT matchs.qualification FROM matchs WHERE matchs.userid_qualificator = :calificated AND matchs.userid_qualificated = :calificator"
    row = await client_db.fetch_one(query = query, values={"calificated": calificated,"calificator": calificator}) 
	#TODO falta contemplar caso que la row no exista, en ese caso debe retornar false!!!
    if not row:
       #print("la otra persona todavía no dió like o dislike a tu perfil")
       return False
    return row["qualification"]=="like" or row["qualification"]=="superlike"  	
	
def send_match_notification(userid_qualificator,userid_qualificated):
    body = 'Hiciste match'
    send_push_notification(userid_qualificated,'Nuevo match', body,{'Match': userid_qualificator,'Tipo': "Match"})
    send_push_notification(userid_qualificator,'Nuevo match', body,{'Match': userid_qualificated,'Tipo': "Match"}) 	
	
#def regular_user_push_notification(originid,destinationid,title, body,data):	
#    title = 'Nuevo like'
#    body = 'Alguien te dio like'
#
#    data = {
#    'Match': originid,
#    'Tipo': "Like"
#    }	
#	
#    send_push_notification(destinationid,title, body,data)	

#def premium_user_push_notification(destinationid,title, body,data):	
#    title = 'Nuevo like'
#    body = 'Alguien te dio like'
#
#    data = {
#    'Match': originid,
#    'Tipo': "Like"
#    }	
#	
#    send_push_notification(destinationid,title, body,data)	
	
@router.post("/user/match/profile",summary="Crea un nuevo perfil", response_model=Profile)
async def create_profile(new_profile:Profile,client_db = Depends(client.get_db)): 
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
        await client_db.execute(client.filters.insert().values(userid = new_profile.userid))

        query_2="SELECT * FROM profiles WHERE profiles.userid = :id"
        result = await client_db.fetch_one(query = query_2, values={"id": new_profile.userid})

        print(tuple(result.values()))    
        profile=profile_schema(result) 
        logger.info(profile)	
        return profile		
    except Exception as e:
        print(e)
        logger.error(e)
        raise HTTPException(status_code=400,detail="El perfil ya existe")

@router.put("/user/{id}/match/profile/",summary="Actualiza el perfil solicitado", response_model=Profile)
async def update_profile(updated_profile:Profile,client_db = Depends(client.get_db),id: str = Path(..., description="El id del usuario")):     
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
        
        query_2="SELECT * FROM profiles WHERE profiles.userid = :id"
        result = await client_db.fetch_one(query = query_2, values={"id": updated_profile.userid})	

        print(tuple(result.values()))    
        profile=profile_schema(result) 
        logger.info(profile)	
        return profile		
    except Exception as e:
        print(e)
        logger.error(e)
        raise HTTPException(status_code=404,detail="No se ha encontrado el perfil") 	

@router.put("/user/{id}/match/profile/block",summary="Bloquea el perfil solicitado", response_model=Profile)
async def block_profile(id: str = Path(..., description="El id del usuario"), client_db = Depends(client.get_db)):     
    logger.info("bloquea el perfil en base de datos")
    profiles = client.profiles
    query = profiles.update().where(profiles.columns.userid == id).values(
        blocked = True
    )
    try: 	
        await client_db.execute(query)		
        
        query_2="SELECT * FROM profiles WHERE profiles.userid = :id"
        result = await client_db.fetch_one(query = query_2, values={"id": id})	

        print(tuple(result.values()))    
        profile=profile_schema(result) 
        logger.info(profile)	
        return profile		
    except Exception as e:
        print(e)
        logger.error(e)
        raise HTTPException(status_code=404,detail="No se ha encontrado el perfil") 		
    
@router.put("/user/{id}/match/profile/unblock",summary="Desbloquea el perfil solicitado", response_model=Profile)
async def unblock_profile(id: str = Path(..., description="El id del usuario"), client_db = Depends(client.get_db)):     
    logger.info("desbloquea el perfil en base de datos")
    profiles = client.profiles
    query = profiles.update().where(profiles.columns.userid == id).values(
        blocked = False
    )
    try: 	
        await client_db.execute(query)		
        
        query_2="SELECT * FROM profiles WHERE profiles.userid = :id"
        result = await client_db.fetch_one(query = query_2, values={"id": id})	

        print(tuple(result.values()))    
        profile=profile_schema(result) 
        logger.info(profile)	
        return profile		
    except Exception as e:
        print(e)
        logger.error(e)
        raise HTTPException(status_code=404,detail="No se ha encontrado el perfil") 		

@router.get("/user/{id}/match/profile/",summary="Obtiene el perfil solicitado", response_model=Profile)
async def view_profile(id: str = Path(..., description="El id del usuario"), client_db = Depends(client.get_db)):     
    logger.info("obteniendo el perfil solicitado")

    try: 	
        query = "SELECT * FROM profiles WHERE profiles.userid = :id"
        result = await client_db.fetch_one(query = query, values={"id": id})

        profile=profile_schema(result) 
        logger.info(profile)	
        return profile
    except Exception as e:
        print(e)
        logger.error(e)
        raise HTTPException(status_code=404,detail="No se ha encontrado el perfil") 		

#@router.post("/user/match/suscription",summary="Suscribe un token a un topic en particular", response_class=Response)		
#async def suscribe(token:str,topic:str)-> None:
#    tokens=[token]
#    response = messaging.subscribe_to_topic(tokens, topic) 
#    if response.failure_count > 0:  
#        raise HTTPException(status_code=400,detail="Falló la suscripción del token "+token+" al topic "+topic)		

#@router.post("/user/match/unsuscription",summary="Desuscribe un token a un topic en particular", response_class=Response)		
#async def unsuscribe(token:str,topic:str)-> None:
#    tokens=[token]
#    response = messaging.unsubscribe_from_topic(tokens, topic) 
#    if response.failure_count > 0:  
#        raise HTTPException(status_code=400,detail="Falló la desuscripción del token "+token+" al topic "+topic)		
		
@router.post("/user/match/notification",summary="Notificar que se envio un mensaje", response_class=Response)
async def notification(userid_sender:str,userid_reciever:str,client_db = Depends(client.get_db))-> None:
    logger.info("notificando envío de mensaje")

    sql_query = '''
        update matchs 
        set last_message_date = NOW() 
        where matchs.userid_qualificator = :sender and matchs.userid_qualificated = :reciever or 
              matchs.userid_qualificator = :reciever and matchs.userid_qualificated = :sender
    '''
    await client_db.execute(query = sql_query, values = { 
        "sender": userid_sender,
        "reciever": userid_reciever
    })

    title = 'Nuevo mensaje'
    body = 'Has recibido un nuevo mensaje'

    data = {
    'Match': userid_sender,
    'Tipo': "Mensaje"
    }	
	
    send_push_notification(userid_reciever,title, body,data)
#    send_push_notification("message",title, body)

@router.post("/user/match/block",summary="Bloquear un usuario", response_class=Response)
async def block_user(userid_bloquer:str,userid_blocked:str,client_db = Depends(client.get_db))-> None:
    logger.info("bloqueando usuario")

    sql_query = '''
        update matchs 
        set blocked = TRUE 
        where matchs.userid_qualificator = :blocker and matchs.userid_qualificated = :blocked
    '''
    await client_db.execute(query = sql_query, values = { 
        "blocker": userid_bloquer,
        "blocked": userid_blocked
    })

@router.put("/user/match/block",summary="Cambiar el estado de bloqueo de un match", response_model=SwipesOut)
async def change_match_block_state(request: PutBlockRequest, client_db = Depends(client.get_db)):
    logger.info("cambiando el estado de bloqueo de un match")
    return await update_block_state(request, client_db)

@router.get("/match/swipes",response_model=List[SwipesOut],summary="Retorna una lista con todos los matchs")
async def get_match_swipes(    
    swiper_id: Union[str, None] = None,
    swiped_id: Union[str, None] = None,
    swiper_names: Union[str,None] = None,
    superlikes: Union[bool, None] = None,
    matchs: Union[bool, None] = None,
    pending: Union[bool, None] = None,
    likes: Union[bool, None] = None,
    dislikes: Union[bool, None] = None,
    blocked: Union[bool, None] = None,
    client_db = Depends(client.get_db)
    ):
    #logger.info("retornando lista con todos los matchs")    
    return await get_swipes_list(swiper_id, swiped_id, swiper_names, superlikes, matchs, pending, likes, dislikes, blocked, client_db)

@router.get("/user/{id}/match/filter/",summary="Obtiene el filtro solicitado", response_model=MatchFilter)
async def view_filter(id: str = Path(..., description="El id del usuario"), client_db = Depends(client.get_db)):
    logger.info("obteniendo filtro solicitado")

    query = "SELECT * FROM filters WHERE filters.userid = :id"
    result = await client_db.fetch_one(query = query, values={"id": id})

#    return filter_schema(result)
    filter=filter_schema(result)
    logger.info(filter)
    return filter

@router.put("/user/{id}/match/filter/",summary="Actualiza el filtro solicitado", response_model=MatchFilter)
async def update_filter(matchfilter: MatchFilter, client_db = Depends(client.get_db),id: str = Path(..., description="El id del usuario")):
    filters = client.filters
    query = filters.update().where(filters.columns.userid == matchfilter.userid).values(
        gender     = matchfilter.gender,
        age_from   = matchfilter.age_from,
        age_to     = matchfilter.age_to,
        education  = matchfilter.education,
        ethnicity  = matchfilter.ethnicity,
        distance   = matchfilter.distance
    )

    logger.info("Actualizando el filtro en base de datos")
    try: 	
        await client_db.execute(query)

        query = "SELECT * FROM filters WHERE filters.userid = :id"
        result = await client_db.fetch_one(query = query, values={"id": matchfilter.userid})

#        return filter_schema(result)
        filter=filter_schema(result)
        logger.info(filter)
        return filter
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=404,detail=str(e))

@router.put("/whitelist",summary="Actualiza la whitelist del servicio")
async def updateWhitelist(whitelist: PutWhiteList):
    logger.info("actualizando whitelist del servicio")

    update_whitelist(whitelist)
    return Response(status_code=201,content="Lista actualizada")

@router.get(
        "/user/match/metrics",
        response_model=List[MatchOut],
        summary="Retorna una lista con todas las metricas de match")
async def view_metrics(client_db = Depends(client.get_db)):
    #logger.info("retornando lista de likes")
    logger.info("retornando lista con todas las metricas de match")

    sql_likes_v_match = '''
        Select Count(1) Likes,
                Count(dest.userid_qualificator) Matches,
                Count(orig.last_message_date) Chats
        from matchs orig
           left  join matchs dest on orig.userid_qualificated = dest.userid_qualificator 
                                 and orig.userid_qualificator = dest.userid_qualificated
                                 and dest.qualification in (:like, :superlike)
                                 and not dest.blocked
        where orig.qualification in (:like, :superlike)
          and not orig.blocked 
    '''
    likes_v_match = await client_db.fetch_all(query = sql_likes_v_match, values = {"like":"like", "superlike":"superlike"})
    
    metrics= {
        "CantMatch": likes_v_match["Matches"],
        "LikesToMatchConversion": likes_v_match["Matches"] / likes_v_match["Likes"],
        "MatchToChatConversion": 0 if (likes_v_match["Matches"] == 0) else (likes_v_match["Chats"] / likes_v_match["Matches"]),
    }
    logger.info(metrics)
    return metrics