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
           return {  "userid": "4321",
  "username": "Angelina Jolie",
  "gender": "Mujer",
  "looking_for": "Hombre",
  "age": 48,
  "education": "Estudios universitarios",
  "ethnicity": "",
  "is_match_plus": False,
  "latitud": 5.3432,
  "longitud": 7.846,
  "last_like_date":'',
  "like_counter": 0,
  "superlike_counter": 0
        }
		
    async def fetch_all(self,query,values):
        #sql_query = '''
        #Select orig.userid_qualificator userid_1, orig.userid_qualificated userid_2,
        #       orig.qualification qualification_1, dest.qualification qualification_2,
        #       orig.qualification_date qualification_date_1, dest.qualification_date qualification_date_2,
        #       pf1.username username_1, pf2.username username_2
        #from matchs orig
        #   inner join profiles pf1 on orig.userid_qualificator = pf1.userid
        #   inner join matchs dest on orig.userid_qualificated = dest.userid_qualificator 
        #                         and orig.userid_qualificator = dest.userid_qualificated
        #   inner join profiles pf2 on orig.userid_qualificated = pf2.userid
        #where orig.qualification = :like
        #  and dest.qualification = :like
        #  and orig.userid_qualificator = :id
        #  and not orig.blocked and not dest.blocked
        #order by orig.last_message_date desc
        #'''
        #print(query==sql_query)		
        #if(query==sql_query):
        #   print("..entra aca..")			
           return self.execute_match_query(values)
		   
    def execute_match_query(self,values):
        #print("valores:")
        #print(values)
        #print(type(values))	
        if(values['id']=="4321"):
           print("entra aca...")
           matchs=[]
           item={
      "userid_1": "4321",
      "username_1": "Angelina Jolie",
      "qualification_1": "like",
      "qualification_date_1": "2024-06-05T23:24:11.580459",
      "userid_2": "3",
      "username_2": "Ryan Gosling",
      "qualification_2": "like",
      "qualification_date_2": "2024-06-06T17:55:48.670889"
      }         		   
           matchs.append(item)
           return matchs