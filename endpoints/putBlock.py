from http.client import HTTPException
from pydantic import BaseModel
from endpoints.getSwipes import get_swipes_list

# Entidad para definir los perfiles
class PutBlockRequest(BaseModel):
   swiper_userid: str
   swiped_userid: str
   isBlocked: bool

async def update_block_state(request: PutBlockRequest,client_db: any):
    
    values = {
        "swiper_userid": request.swiper_userid,
        "swiped_userid": request.swiped_userid,
    }

    get_blocked_rows = '''
        SELECT *
            FROM matchs  
            WHERE ( matchs.userid_qualificator = :swiper_userid AND matchs.userid_qualificated = :swiped_userid )
               OR ( matchs.userid_qualificator = :swiped_userid AND matchs.userid_qualificated = :swiper_userid )
    '''

    rows = await client_db.fetch_all(query = get_blocked_rows, values = values)

    values['isBlocked'] = request.isBlocked

    if ( len(rows) == 0 ):
        raise HTTPException(status_code=404,detail="No se ha encontrado el match.") 		

    # Here should I create the block for the other user?

    # if ( len(rows) == 1 and rows[0]['userid_qualificator'] == request.swiper_userid ):

    #     insert_empty_qualificated_user = '''
    #         INSERT INTO matchs SET 
    #             userid_qualificator = :swiped_userid, 
    #             userid_qualificated = :swiper_userid, 
    #             blocked = :isBlocked
    #     '''
    #     await client_db.execute(query = insert_empty_qualificated_user, values = values)


    # if ( len(rows) == 1 and rows[0]['userid_qualificated'] == request.swiper_userid ):

    #     insert_empty_qualificator_user = '''
    #         INSERT INTO matchs
    #         	SET userid_qualificated = :swiped_userid, userid_qualificator = :swiper_userid, blocked = :isBlocked
    #     '''
    #     await client_db.execute(query = insert_empty_qualificator_user, values = values)

    update_block_status = '''
        UPDATE matchs 
        SET blocked = :isBlocked
        WHERE ( matchs.userid_qualificator = :swiper_userid AND matchs.userid_qualificated = :swiped_userid )
           OR ( matchs.userid_qualificator = :swiped_userid AND matchs.userid_qualificated = :swiper_userid )
    '''

    await client_db.execute(query = update_block_status, values = values)

    swipes = await get_swipes_list(
        swiper_id = request.swiper_userid,
        swiped_id = request.swiped_userid,
        swiper_names = None,
        superlikes = None,
        matchs = None,
        pending = None,
        likes = None,
        dislikes = None,
        blocked = None,
        client_db = client_db
    )

    return swipes[0]