from data.profile import Filter
import data.client as client

class FilterData:
    
    def __init__(self, client_db):
        self.client_db = client_db

    async def get_by_id(self, id:str):
        return await self.client_db.fetch_one(
            query = "SELECT * FROM filters WHERE filters.userid = :id", 
            values={"id": id}
        )
    
    async def update(self, newvalues: Filter):
        filters = self.client_db.filters
        query = filters.update().where(
            filters.columns.userid == newvalues.userid
        ).values(
            userid    = newvalues.userid,
            gender    = newvalues.gender,
            age_from  = newvalues.age_from,
            age_to    = newvalues.age_to,
            education = newvalues.education,
            ethnicity = newvalues.ethnicity,
            distance  = newvalues.distance
        )

        await self.client_db.execute(query = query)
    
    async def new(self, userid:str):
        instruction = self.client_db.filters.insert().values(
            userid    = userid,
            gender    = None,
            age_from  = None,
            age_to    = None,
            education = None,
            ethnicity = None,
            distance  = None
        )
        await self.client_db.execute(instruction)