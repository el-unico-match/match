import logging
from settings import settings
logging.basicConfig(filename=settings.log_filename, level=settings.logging_level, format='%(asctime)s - %(levelname)s - %(message)s')

from fastapi import FastAPI
from routers import match_db
from data.apikey import enableApiKey
from middlewares.ingoingSecurityCheck import IngoingSecurityCheck
from middlewares.outgoingSecurityCheck import OutgoingSecurityCheck
import asyncio

summary="Microservicio que se encarga de todo lo relativo a match"

app=FastAPI(
    title="match",
    version="0.0.11",
    summary=summary,
    docs_url='/api-docs'
)

app.add_middleware(IngoingSecurityCheck)
app.add_middleware(OutgoingSecurityCheck)

# Para iniciar el server hacer: uvicorn main:app --reload
app.include_router(match_db.router)


# if settings.mode=='production':
asyncio.create_task(enableApiKey())

# HTTP response
# 100 información
# 200 las cosas han ido bien
# 201 se ha creado algo
# 204 no hay contenido
# 300 hay una redireccion
# 304 no hay modificaciones 
# 400 error
# 404 no encontrado
# 500 error interno

