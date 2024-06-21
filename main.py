from fastapi import FastAPI
from routers import match_db

summary="Microservicio que se encarga de todo lo relativo a match"

app=FastAPI(
    title="match",
    version="0.0.11",
    summary=summary,
    docs_url='/api-docs'
)

# Para iniciar el server hacer: uvicorn main:app --reload

# Routers (subconjuntos dentro de la API principal)
#if settings.disable_db==True:
#   print("no usa bd")
#   app.include_router(match.router)
#else:
#   print("usa bd")
#   app.include_router(match_db.router)
app.include_router(match_db.router)

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

