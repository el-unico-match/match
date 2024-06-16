from sqlalchemy import inspect, text
from data.client import engine, matchs, profiles

class memoryDatabase:

    def __init__(self):
       self.database = engine.connect()

    async def execute(self, query, values):
        self.database.execute(text(query), values)

    async def fetch_all(self, query, values):
        with self.database.execute(text(query), values) as proxy:
            keys = proxy.keys()
            return [{key: value for key, value in zip(keys, row)} for row in proxy.fetchall()]
        
    def insertProfile(self, profile):
        self.database.execute(profiles.insert(), profile)

    def insertSwipe(self, swipe):
        self.database.execute(matchs.insert(),swipe)

    def __del__(self):
        self.database.close()
