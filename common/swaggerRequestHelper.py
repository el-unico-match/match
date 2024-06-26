from fastapi import Request
from urllib.parse import urlparse

def isRequestSentFromSwagger(request: Request):
    refererPath = urlparse(request.headers.get('Referer','')).path
    urlPath = request.url.path.lower()

    isRequestSentFromSwagger = urlPath.startswith('/api-docs') or refererPath.startswith('/api-docs') or urlPath.startswith('/openapi.json') 

    return isRequestSentFromSwagger