from fastapi import APIRouter,Path,Depends,Response,HTTPException
from typing import List
from bson import ObjectId
from settings import Settings
#import logging
import data.client as client

settings=Settings()

#logging.basicConfig(filename=settings.log_filename,level=settings.logging_level)
#logger=logging.getLogger(__name__)  
			
router=APIRouter(tags=["match"])


# Operaciones de la API

@router.get("/status",summary="Retorna el estado del servicio")
async def view_status(): 
    logger.info("retornando status")
    return {"status":"ok"}

@router.get("/user/{id}/matchs")
async def view_matchs(id:str,client_db = Depends(client.get_db)):
    print("Implementar lista de matchs")
	
@router.get("/user/{id}/matchs/filter")
async def filter(id:str,gender:str,age:int,education:str,ethnicity:str,client_db = Depends(client.get_db)):
    print("Implementar filtro")
	
@router.get("/user/{id}/match/preference")
async def define_preference(id:str,gender:str,age:int,education:str,ethnicity:str,client_db = Depends(client.get_db)):
    print("Implementar funcionalidad de like y dislike")