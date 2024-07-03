from fastapi import HTTPException
from sqlalchemy import func, tuple_
from datetime import datetime

class Mock:

    def __init__(self):
        self.standard_user_profile={  "userid": "100",
                     "username": "Angelina Jolie",
                     "gender": "Mujer",
                     "looking_for": "Hombre",
                     "age": 48,
                     "education": "Estudios universitarios",
                     "ethnicity": "",
                     "is_match_plus": False,
                     "latitud": 5.3432,
                     "longitud": 7.846,
                     "last_like_date":datetime.now(),
                     "like_counter": 4,
                     "superlike_counter": 0
                  } 
				  
        self.premium_user_profile={  "userid": "200",
                     "username": "Margot Robbie",
                     "gender": "Mujer",
                     "looking_for": "Hombre",
                     "age": 33,
                     "education": "Estudios secundarios",
                     "ethnicity": "",
                     "is_match_plus": True,
                     "latitud": 6.5472,
                     "longitud": 4.873,
                     "last_like_date":datetime.now(),
                     "like_counter": 4,
                     "superlike_counter": 5
                  } 		
    async def execute(self,query):
	    #print(query)
	    print("no hace nada")
	    pass
		
    async def fetch_one(self,query,values):
        if(query=="SELECT * FROM profiles WHERE profiles.userid = :id"):
           return self.execute_profile_query(values)
        if(query=="SELECT * FROM filters WHERE filters.userid = :id"):
           return self.execute_filter_query(values)	
		   
    def execute_profile_query(self,values):
        #print("valores:")
        #print(values)
        #print(type(values))	
        if(values['id']=="100"):
           return self.standard_user_profile		
        elif(values['id']=="200"):
           return self.premium_user_profile				   
        else:
           raise Exception#raise HTTPException(status_code=404,detail="No se ha encontrado el perfil") 


    def execute_filter_query(self,values):
        #print("valores:")
        #print(values)
        #print(type(values))		
        if(values['id']=="100"):
           return {  "userid": "100",
  "gender": "Hombre",
  "age_from": 28,
  "age_to":48,
  "education": "",
  "ethnicity": "",
  "distance": 100,
        }		
        else:
           raise Exception#raise HTTPException(status_code=404,detail="No se han encontrado filtros con ese id") 

		
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
        if(values['id']=="100"):
           #print("entra aca...")
           matchs=[]
           item={
      "userid_1": "100",
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