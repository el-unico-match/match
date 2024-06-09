from model.match import Match
import model.client as client

class MatchData:
    def __init__(self, client_db):
        self.client_db = client_db

    async def including_user(self, userid:str):
        return await self.client_db.fetch_one(
            query = "SELECT * FROM filters WHERE filters.userid = :id", 
            values={"id": userid}
        )
    
    async def get_matches(self, userid:str):
        return await self.client_db.fetch_all(query = '''
            Select orig.userid_qualificator userid_1, orig.userid_qualificated userid_2,
                orig.qualification qualification_1, dest.qualification qualification_2,
                orig.qualification_date qualification_date_1, dest.qualification_date qualification_date_2,
                pf1.username username_1, pf2.username username_2
            from matchs orig
            inner join profiles pf1 on orig.userid_qualificator = pf1.userid
            inner join matchs dest on orig.userid_qualificated = dest.userid_qualificator 
                                    and orig.userid_qualificator = dest.userid_qualificated
            inner join profiles pf2 on orig.userid_qualificated = pf2.userid
            where orig.qualification = :like
            and dest.qualification = :like
            and orig.userid_qualificator = :id
            and not orig.blocked and not dest.blocked
            order by orig.last_message_date desc
        ''', values = { "id": userid, "like": "like" })
    
    async def block_user(self, userid_from:str, userid_to:str):
        sql_query = '''
            update matchs 
            set blocked = TRUE 
            where matchs.userid_qualificator = :blocker and matchs.userid_qualificated = :blocked
        '''
        await self.client_db.execute(query = sql_query, values = { 
            "blocker": userid_from,
            "blocked": userid_to
        })
    
    async def nofity_message(self, userid_from:str, userid_to:str):
        sql_query = '''
            update matchs 
            set last_message_date = NOW() 
            where matchs.userid_qualificator = :sender and matchs.userid_qualificated = :reciever or 
                matchs.userid_qualificator = :reciever and matchs.userid_qualificated = :sender
        '''
        await self.client_db.execute(query = sql_query, values = { 
            "sender": userid_from,
            "reciever": userid_to
        })

    async def add_or_update(self, values:Match):
        matchs = client.matchs

        # Por las dudas pero no deberia pasar
        # porque solo se muestran para hacer match los que no fueron calificados
        old_del = matchs.delete().where(
            matchs.columns.userid_qualificator == values.userid_qualificator,
            matchs.columns.userid_qualificated == values.userid_qualificated
        )
        await self.client_db.execute(old_del)

        action = matchs.insert().values(
            userid_qualificator = values.userid_qualificator,
            userid_qualificated = values.userid_qualificated,
            qualification = values.qualification,
            blocked = False,
            qualification_date = values.now(),
        )
        await self.client_db.execute(action)