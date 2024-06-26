import logging
from settings import settings
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from common.swaggerRequestHelper import isRequestSentFromSwagger

logger=logging.getLogger(__name__)

class IngoingSecurityCheck(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):

        try:
            isApiKeyAllowed = settings.isIngoingSecurityCheckEnabled == False or \
                ( (settings.isIngoingSecurityCheckEnabled == True) and ('x-apikey' in request.headers) and (request.headers['x-apikey'] in settings.apikey_whitelist) )

            if ( isRequestSentFromSwagger(request) == True or  isApiKeyAllowed == True ):
                response = await call_next(request)
                return response

            elif ( 'x-apikey' in request.headers ) == False:
                error_message = 'Encabezado x-apikey faltante.'
                logger.error(error_message)
                return Response(content=error_message, status_code=400)
            
            else:
                error_message = 'Servicio no disponible.'
                logger.error(error_message)
                return Response(content=error_message, status_code=503)
     
        except Exception as e500:
            exceptionJson = jsonable_encoder(e500)
            logger.error(exceptionJson, str(e500), exc_info=True)
            return Response(content='Lo sentimos, algo falló', status_code=500)

