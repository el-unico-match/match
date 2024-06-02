from data.match import SwipesOut
from typing import Union

def swipe_likes_schema(result)-> dict:
    schema= {
        "is_match": result["is_match"],
        "qualificator_id": result["id_1"],
        "qualificator_name": result["name_1"],
        "qualificator_swipe": result["swipe_1"],
        "qualificator_date": str(result["date_1"]),
        "qualificator_blocked": result["blocker_2"] if result["blocker_2"] is not None else False,
        "qualificated_id": result["id_2"],
        "qualificated_name": result["name_2"],
        "qualificated_swipe": result["swipe_2"] if result["blocker_2"] is not None else "",
        "qualificated_date": str(result["date_2"]) if result["date_2"] is not None else "",
        "qualificated_blocked": result["blocker_1"] if result["blocker_1"] is not None else False,
    }

    return schema

def swipe_result(results)-> list:
   list=[]
   for result in results:
       list.append(SwipesOut(**swipe_likes_schema(result)))
   return list	
	
async def get_swipes_list(
    swiper_id: Union[str, None],
    swiper_name: Union[str,None],
    superlikes: Union[bool, None],
    matchs: Union[bool, None],
    client_db: any):

    values = { 
        # 'id': swiper_id,
        # 'name': swiper_name,
        # 'match': matchs,
        # "superlike": superlikes,
    }

    query = \
        'SELECT '\
        '	pf1.username name_1, '\
        ' 	orig.userid_qualificator id_1, '\
        '   orig.qualification swipe_1, '\
        '	orig.qualification_date date_1, '\
        '	orig.blocked blocker_1, '\
        '	pf2.username name_2, '\
        '	orig.userid_qualificated id_2, '\
        ' 	dest.qualification swipe_2, '\
        '	dest.qualification_date date_2, '\
        '	dest.blocked blocker_2, '\
        '	CASE WHEN '\
        '		orig.qualification_date IS NOT NULL AND '\
        '		orig.blocked = \'false\' AND'\
        '		dest.qualification_date IS NOT NULL AND '\
        '		dest.blocked = \'false\' '\
        '	THEN \'true\' ELSE \'false\' END AS is_match '\
        '   FROM matchs orig  '\
        '        LEFT JOIN matchs AS dest ON orig.userid_qualificated = dest.userid_qualificator AND orig.userid_qualificator = dest.userid_qualificated '\
        '		 INNER JOIN profiles AS pf1 ON pf1.userid = orig.userid_qualificator '\
        '        INNER JOIN profiles AS pf2 ON pf2.userid = orig.userid_qualificated '\
        ' 		 WHERE dest.qualification_date IS NULL OR orig.qualification_date < dest.qualification_date '\
        '        ORDER BY is_match DESC, dest.qualification_date DESC, orig.qualification_date DESC'

    data = await client_db.fetch_all(query, values)

    results = swipe_result(data) 

    return results