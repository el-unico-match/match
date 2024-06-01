from fastapi import APIRouter,Path,Depends,Response,HTTPException
#from data.schemas.profile import Profile
#from data.models.profile import profiles as profiles_model
from data.match import Match,MatchIn,MatchOut
from data.profile import Profile
from typing import List,Union
from bson import ObjectId
from settings import Settings
from sqlalchemy import and_
#import logging
import data.client as client

settings=Settings()

#logging.basicConfig(filename=settings.log_filename,level=settings.logging_level)
#logger=logging.getLogger(__name__)  
			
def profile_schema(profile)-> dict:
#    print(profile)
#    print(profile["userid"])
#    print(profile["username"])
    schema= {"userid":profile["userid"],
         	"username":profile["username"],
	        "email":profile["email"],
			"description":profile["description"],
			"gender":profile["gender"],
			"looking_for":profile["looking_for"],
			"age":int(profile["age"]),
			"education":profile["education"],
	        "ethnicity":profile["ethnicity"]
			}
#    print("schema:")
#    print(schema)
#    print(type(schema))
    return schema			

def profiles_schema(profiles)-> list:
   list=[]
   for profile in profiles:
       list.append(Profile(**profile_schema(profile)))
   return list			

def match_schema(match)-> dict:
#    print(profile)
#    print(profile["userid"])
#    print(profile["username"])
    schema= {"id":match["id"],
         	"userid_1":match["userid_1"],
	        "qualification_1":match["qualification_1"],
			"userid_2":match["userid_2"],
			"username_2":match["username_2"],
			"qualification_2":match["qualification_2"]
			}
#    print("schema:")
#    print(schema)
#    print(type(schema))
    return schema

def matchs_schema(matchs)-> list:
   list=[]
   for match in matchs:
       list.append(MatchOut(**match_schema(match)))
   return list	
	
router=APIRouter(tags=["match administration"])

@router.get("/user/matchs",response_model=List[MatchOut]
,summary="Retorna una lista con todos los matchs")
async def view_matchs(client_db = Depends(client.get_db)):
#    print("Implementar lista de matchs")
#   matchs=[]
#   matchs.append(
#   Match(matchid = "66304a6b2891cdcfebdbdc6f",
#   userid_1 = "1",
#   qualification_1 = "like",
#   userid_2 = "2",
#   qualification_2 = "like"))
#   return matchs
#    query = client.matchs.filter(matchs.userid_1==id,matchs.qualification_1 == "like",matchs.qualification_2 == "like")
##    matchs=client.matchs
##    query = matchs.select().where(and_(matchs.columns.userid_1==id,matchs.columns.qualification_1 == "like",matchs.columns.qualification_2 == "like") )
#    query = matchs.select().where(matchs.columns.qualification_2 == "like")
    select_clause=' SELECT matchs.id,matchs.userid_1,matchs.qualification_1,matchs.userid_2,profiles.username as username_2,matchs.qualification_2'
    from_clause=' FROM profiles'
    join_clause=' FULL OUTER JOIN matchs ON matchs.userid_2 = profiles.userid'
    where_clause=' WHERE matchs.qualification_1 = :qualification AND matchs.qualification_2 = :qualification'
    matchs_results = select_clause+from_clause+join_clause+where_clause
#    return await client_db.fetch_all(query)
    results=await client_db.fetch_all(query=matchs_results,values={"qualification":"like"})
    for result in results:
	    print(tuple(result.values()))
    return matchs_schema(results) 