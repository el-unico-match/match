from fastapi import HTTPException
from model.profile import Profile
from data.filter_data import FilterData
from datetime import datetime
from settings import settings
import model.client as client

class ProfileData:
    
    def __init__(self, client_db):
        self.client_db = client_db

    async def get_by_id(self, userid:str):
        myprofile = await self.client_db.fetch_one(
            query = "SELECT * FROM profiles WHERE profiles.userid = :id", 
            values={"id": userid}
        )

        print(myprofile)
        if not myprofile:
            raise HTTPException(status_code=404,detail="No se han encontrado perfiles con ese id")
        return myprofile
    

    async def get_valid_candidates(self, userid:str):
        filterdata = FilterData(self.client_db)
        myfilter = await filterdata.get_by_id(userid)

        arguments = { 'id': userid, "superlike":"superlike" }
        sql_query = '''
            Select pf.*
            from profiles pf
            left join matchs m on m.userid_qualificator = :id and pf.userid = m.userid_qualificated
            left join matchs m2 on
                                m2.userid_qualificated = :id
                                and pf.userid = m2.userid_qualificator
                                and m2.qualification = :superlike
            where pf.userid <> :id and m.id is null
        '''
            
        if (myfilter.gender != None):
            sql_query += ' and pf.gender = :gender'
            arguments["gender"] = myfilter.gender
        
        if (myfilter.age_from != None):
            sql_query += ' and pf.age >= :age_from'
            arguments["age_from"] = myfilter.age_from
        
        if (myfilter.age_to != None):
            sql_query += ' and pf.age <= :age_to'
            arguments["age_to"] = myfilter.age_to
        
        if (myfilter.education != None):
            sql_query += ' and pf.education = :education'
            arguments["education"] = myfilter.education
        
        if (myfilter.ethnicity != None):
            sql_query += ' and pf.ethnicity = :ethnicity'
            arguments["ethnicity"] = myfilter.ethnicity

        sql_query += ' order by m2.userid_qualificator desc, pf.is_match_plus desc, pf.userid'
        
        return await self.client_db.fetch_all(query = sql_query, values = arguments)
    
    async def spend_likes(self, userid:str, liketype: str):
        myprofile = await self.get_by_id(userid)

        newvalues = {
            "id": userid,
            "last_like_date": myprofile["last_like_date"],
            "like_counter": myprofile["like_counter"],
            "superlike_counter": myprofile["superlike_counter"],
        }

        if (not myprofile['is_match_plus']):
            if (liketype == 'superlike'):
                raise HTTPException(status_code=400,detail="Usuario normal no puede dar superlikes")

            if (myprofile['last_like_date'].date() < datetime.now().date()):
                newvalues['like_counter'] = 0

            if (liketype == 'like' and newvalues['like_counter'] > settings.LIKE_LIMITS):
                raise HTTPException(status_code=400,detail="Se alcanzo el limite de likes")
            
            if (liketype == 'like'):
                newvalues['last_like_date'] = datetime.now()
                newvalues['like_counter'] += 1
        else:
            if (myprofile['last_like_date'].date() < datetime.now().date()):
                newvalues['superlike_counter'] = 0
            
            if (liketype == 'superlike' and newvalues['superlike_counter'] > settings.SUPERLIKE_LIMITS):
                raise HTTPException(status_code=400,detail="Se alcanzo el limite de superlikes")
            
            if (liketype == 'superlike'):
                newvalues['last_like_date'] = datetime.now()
                newvalues['superlike_counter'] += 1

        query = '''
            update profiles 
            set last_like_date = :last_like_date,
                superlike_counter = :superlike_counter,
                like_counter = :like_counter
            where userid = :id
        '''

        await self.client_db.execute(query = query, values = newvalues)
    

    async def new(self, new_profile: Profile):
        await self.client_db.execute(client.profiles.insert().values(userid = new_profile.userid,
            username          = new_profile.username,
            gender            = new_profile.gender,
            looking_for       = new_profile.looking_for,
            age               = new_profile.age,
            education         = new_profile.education,
            ethnicity         = new_profile.ethnicity,
            is_match_plus     = False,
            latitud           = new_profile.latitud,
            longitud          = new_profile.longitud,
            last_like_date    = datetime.now(),
            like_counter      = new_profile.like_counter,
            superlike_counter = new_profile.superlike_counter
        ))
    
    async def update(self, values: Profile):
        profiles = client.profiles
        query = profiles.update().where(profiles.columns.userid == values.userid).values(
            username          = values.username,
            gender            = values.gender,
            looking_for       = values.looking_for,
            age               = values.age,
            education         = values.education,
            ethnicity         = values.ethnicity,
            is_match_plus     = values.is_match_plus,
            latitud           = values.latitud,
            longitud          = values.longitud,
            like_counter      = values.like_counter,
            superlike_counter = values.superlike_counter
        )

        await self.client_db.execute(query)