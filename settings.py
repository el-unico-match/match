from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    disable_db:bool=False
	
    log_filename:str='match.log'
    NOTSET:int=0
    DEBUG:int=10
    INFO:int=20
    WARNING:int=30
    ERROR:int=40
    CRITICAL:int=50	
    logging_level:int=DEBUG
	
    DOCKER_DOMAIN:str='match_postgres'
    LOCAL_DOMAIN:str='localhost'
    db_domain:str = LOCAL_DOMAIN
    db_port:int = 5000
    db_host:str=db_domain+":"+str(db_port)
    local_db_name:str='local'
    remote_db_name:str='remote'	
    db_name:str=local_db_name
    db_credentials:str=''
	
    LIKE_LIMITS:int=2
    SUPERLIKE_LIMITS:int=4

    model_config = SettingsConfigDict(env_file=("dev.env",".env"))	
