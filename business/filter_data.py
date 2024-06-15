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
    
    async def update(self, values: Filter):
        filters = client.filters
        query = filters.update().where(
            filters.columns.userid == filter.userid
        ).values(
            userid    = filter.userid,
            gender    = filter.gender,
            age_from  = filter.age_from,
            age_to    = filter.age_to,
            education = filter.education,
            ethnicity = filter.ethnicity,
            distance  = filter.distance
        )

        await self.client_db.execute(query = query)
    
    async def new(self, userid:str):
        instruction = client.filters.insert().values(
            userid    = userid,
            gender    = None,
            age_from  = None,
            age_to    = None,
            education = None,
            ethnicity = None,
            distance  = None
        )
        await self.client_db.execute(instruction)