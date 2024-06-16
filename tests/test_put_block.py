import pytest # type: ignore
from datetime import datetime
from endpoints.putBlock import update_block_state, PutBlockRequest
from tests.memory_database import memoryDatabase

user1 = {
    "userid": "id1",
    "username": "name1",
    "gender": "Hombre",
    "looking_for":"Mujer",
    "age":"40",
    "education":"Universitaria",
    "ethnicity":"Vainilla",
    "is_match_plus":True,
    "latitud":23.123123,
    "longitud":12.121223,
    "last_like_date": datetime.now(),
    "like_counter": 0,
    "superlike_counter": 0,
}

user2 = {
    "userid": "id2",
    "username": "name2",
    "gender": "Mujer",
    "looking_for":"Hombre",
    "age":"40",
    "education":"Universitaria",
    "ethnicity":"Vainilla",
    "is_match_plus":False,
    "latitud":23.123123,
    "longitud":12.121223,
    "last_like_date":datetime.now(),
    "like_counter": 0,
    "superlike_counter": 0,
}

user3 = {
    "userid": "id3",
    "username": "name3",
    "gender": "Hombre",
    "looking_for":"Hombre",
    "age":"40",
    "education":"Universitaria",
    "ethnicity":"Vainilla",
    "is_match_plus":False,
    "latitud":23.123123,
    "longitud":12.121223,
    "last_like_date":datetime.now(),
    "like_counter": 0,
    "superlike_counter": 0,
}

user1Like = {
    "userid_qualificator": "id1",
    "userid_qualificated": "id2",
    "qualification": "like",
    "qualification_date": datetime.now(),
    "last_message_date": datetime.now(),
    "blocked": False,
}

user2Like = {
    "userid_qualificator": "id2",
    "userid_qualificated": "id1",
    "qualification": "like",
    "qualification_date": datetime.now(),
    "last_message_date": datetime.now(),
    "blocked": False,
}

user3Like = {
    "userid_qualificator": "id3",
    "userid_qualificated": "id1",
    "qualification": "superlike",
    "qualification_date": datetime.now(),
    "last_message_date": datetime.now(),
    "blocked": False,
}

user3Blocked = {
    "userid_qualificator": "id1",
    "userid_qualificated": "id3",
    "qualification": "dislike",
    "qualification_date": datetime.now(),
    "last_message_date": datetime.now(),
    "blocked": True,
}

@pytest.mark.asyncio
async def test_get_list():
    database = memoryDatabase()
    database.insertProfile(user1)
    database.insertProfile(user2)

    database.insertSwipe(user1Like)
    database.insertSwipe(user2Like)

    request = PutBlockRequest(
        swiper_userid = user1["userid"],
        swiped_userid = user2["userid"],
        isBlocked = True,
    )

    element1 = await update_block_state(
        request,
        client_db=database
    )

    assert element1.is_match is True
    assert element1.qualificator_id == "id1"
    assert element1.qualificator_name == "name1"
    assert element1.qualificator_swipe == "like"
    assert element1.qualificator_date == str(user1Like["qualification_date"])
    assert element1.qualificator_blocked is True
    assert element1.qualificated_id == "id2"
    assert element1.qualificated_name == "name2"
    assert element1.qualificated_date == str(user2Like["qualification_date"])
    assert element1.qualificated_blocked is True

@pytest.mark.asyncio
async def test_get_list():
    database = memoryDatabase()
    database.insertProfile(user1)
    database.insertProfile(user2)

    database.insertSwipe(user1Like)
    database.insertSwipe(user2Like)

    request = PutBlockRequest(
        swiper_userid = user1["userid"],
        swiped_userid = user2["userid"],
        isBlocked = False,
    )

    element1 = await update_block_state(
        request,
        client_db=database
    )

    assert element1.is_match is True
    assert element1.qualificator_id == "id1"
    assert element1.qualificator_name == "name1"
    assert element1.qualificator_swipe == "like"
    assert element1.qualificator_date == str(user1Like["qualification_date"])
    assert element1.qualificator_blocked is False
    assert element1.qualificated_id == "id2"
    assert element1.qualificated_name == "name2"
    assert element1.qualificated_date == str(user2Like["qualification_date"])
    assert element1.qualificated_blocked is False


