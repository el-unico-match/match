from fastapi import HTTPException
from sqlalchemy import func, tuple_

class Mock:

    def __init__(self):
        pass     
		
    async def execute(self,query):
	    print("no hace nada")
	    pass
		
    async def fetch_one(self,query,values):
        if(query=="SELECT * FROM profiles WHERE profiles.userid = :id"):
           return self.execute_profile_query(values)
		   
    def execute_profile_query(self,values):
        #print("valores:")
        #print(values)
        #print(type(values))		
        if(values['id']!="4321"):
           raise HTTPException(status_code=404,detail="No se ha encontrado el perfil") 
        else:
           return {"userid": "4321",	
        "username": "Luis",
        "gender": "Hombre",
        "looking_for": "Mujer",
        "age": 33,
        "education": "Universitaria",
        "ethnicity": "",
        "is_match_plus": True,
        "latitud": 23.3223,
        "longitud": 55.82,
        "last_like_date":"",
        "like_counter": 0,
        "superlike_counter": 0
        }