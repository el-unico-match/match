from fastapi.testclient import TestClient
import data.client as client
from main import app
from tests.mocks import Mock

def override_get_db():
   mock=Mock()
   return mock
#    return profiles

#async def override_get_db():
#    await database.connect()
#    try:
#        yield database
#    finally:
#        await database.disconnect()	
#        database.drop()

app.dependency_overrides[client.get_db] = override_get_db

client = TestClient(app)

def test_status():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json()['status'] == "ok"
"""

"""
def test_view_inexistent_user_profile():
    response = client.get("/user/profile/1234")
    assert response.status_code == 404, response.text
	
"""	

"""
def test_create_user_profile():
    response = client.post("/user/match/profile",
	json={
        "userid": "4321",	
        "username": "Angelina Jolie",
        "gender": "Mujer",
        "looking_for": "Hombre",
        "age": 48,
        "education": "Universitaria",
        "ethnicity": "",
        "is_match_plus": False,
        "latitud": 5.3432,
        "longitud": 7.846,
        "like_counter": 4,
        "superlike_counter": 0
    })

    #print(response) 
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["userid"] == "4321"
    assert data["username"] == "Angelina Jolie"
    assert data["gender"] == "Mujer"
    assert data["looking_for"] == "Hombre"
    assert data["age"] == 48
    assert data["education"] == "Estudios universitarios"
    assert data["ethnicity"] == ""	
    assert data["is_match_plus"] == False
    assert data["latitud"] == 5.3432
    assert data["longitud"] == 7.846
    assert data["like_counter"] == 4
    assert data["superlike_counter"] == 0
	
"""

"""

def test_view_profile():
    response = client.get("/user/4321/match/profile")

    #print(response) 
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["userid"] == "4321"
    assert data["username"] == "Angelina Jolie"
    assert data["gender"] == "Mujer"
    assert data["looking_for"] == "Hombre"
    assert data["age"] == 48
    assert data["education"] == "Estudios universitarios"
    assert data["ethnicity"] == ""	
    assert data["is_match_plus"] == False
    assert data["latitud"] == 5.3432
    assert data["longitud"] == 7.846
    assert data["like_counter"] == 4
    assert data["superlike_counter"] == 0

#def test_create_existent_user_profile():
#    response = client.post("/user/profile",
#	json={
#        "userid": "1234",	
#        "username": "Luis",
#        "gender": "Hombre",
#        "looking_for": "Mujer",
#        "age": 33,
#        "education": "Universitaria",
#        "ethnicity": "",
#        "is_match_plus": True,
#        "latitud": 23.3223,
#        "longitud": 55.82,
#        "like_counter": 0,
#        "superlike_counter": 0
#    })
#    assert response.status_code == 404, response.text
	
def test_update_inexistent_user_profile():
    response = client.put("/user/profile/1234",
	json={
  "userid": "1234",
  "username": "Angelina Jolie",
  "gender": "Mujer",
  "looking_for": "Hombre",
  "age": 48,
  "education": "Estudios universitarios",
  "ethnicity": "",
  "is_match_plus": False,
  "latitud": 5.3432,
  "longitud": 7.846,
  "like_counter": 4,
  "superlike_counter": 0
    })
    assert response.status_code == 404, response.text

def test_view_matchs():
    response = client.get("/user/4321/matchs")
    assert response.status_code == 200, response.text
    data = response.json()[0] 
    assert data["myself"]["userid"] == "4321"
    assert data["myself"]["username"] == "Angelina Jolie"
    assert data["myself"]["qualification"] == "like"
    assert data["myself"]["qualification_date"] == "2024-06-05T23:24:11.580459"
    assert data["matched"]["userid"] == "3"
    assert data["matched"]["username"] == "Ryan Gosling"
    assert data["matched"]["qualification"] == "like"	
    assert data["matched"]["qualification_date"] == "2024-06-06T17:55:48.670889"

def test_view_likes():
    response = client.get("/user/4321/likes")
    assert response.status_code == 200, response.text
    data = response.json()[0] 
    assert data["myself"]["userid"] == "4321"
    assert data["myself"]["username"] == "Angelina Jolie"
    assert data["myself"]["qualification"] == "like"
    assert data["myself"]["qualification_date"] == "2024-06-05T23:24:11.580459"
    assert data["matched"]["userid"] == "3"
    assert data["matched"]["username"] == "Ryan Gosling"
    assert data["matched"]["qualification"] == "like"	
    assert data["matched"]["qualification_date"] == "2024-06-06T17:55:48.670889"

def test_update_filter():
    response = client.put("/user/4321/match/filter",
	json={
  "userid": "4321",
  "gender": "Hombre",
  "age_from": 28,
  "age_to":48,
  "education": "",
  "ethnicity": "",
  "distance": 100,
    })

    #print(response) 
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["userid"] == "4321"
    assert data["gender"] == "Hombre"
    assert data["age_from"] == 28
    assert data["age_to"] == 48
    assert data["education"] == ""
    assert data["ethnicity"] == ""	
    assert data["distance"] == 100

def test_define_preference_with_more_likes_than_limit():
    response = client.post("/user/4321/match/preference",
	json={
  "userid_qualificator": "4321",
  "userid_qualificated": "3",
  "qualification": "like"
})

    #print(response) 
    assert response.status_code == 400, response.text
    response = response.text
    print(response)
    assert response == '{"detail":"Se alcanzo el limite de likes"}'
	
#def test_get_inexistent_user_profile_filter():
#    response = client.get("/user/1234/profiles/filter")
#    assert response.status_code == 404, response.text

def test_get_inexistent_user_next_candidate():
    response = client.get("/user/1234/match/nextcandidate")
    assert response.status_code == 404, response.text