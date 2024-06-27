from fastapi.testclient import TestClient
import data.client as client
from main import app
#from tests.mocks import Mocks

#def override_get_db():
#   mocks=Mocks()
#   return mocks
#    return profiles

#app.dependency_overrides[client.get_db] = override_get_db

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
#def test_create_user_profile():
#    response = client.post("/user/profile",
#	json={
#        "userid": "4321",	
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

#    assert response.status_code == 200, response.text
#    data = response.json()[0]
#    assert data["userid"] == "4321"
#    assert data["username"] == "Luis"
#    assert data["gender"] == "Hombre"
#    assert data["looking_for"] == "Mujer"
#    assert data["age"] == 33
#    assert data["education"] == "Universitaria"
#    assert data["ethnicity"] == ""	
#    assert data["is_match_plus"] == True
#    assert data["latitud"] == 23.3223
#    assert data["longitud"] == 55.82
#    assert data["like_counter"] == 0
#    assert data["superlike_counter"] == 0
	
"""

"""

#def test_create_existent_user_profile():
#    response = client.post("/user/profile",
#	json={
#        "userid": "4321",	
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
        "username": "Luis",
        "gender": "Hombre",
        "looking_for": "Mujer",
        "age": 0,
        "education": "Universitaria",
        "ethnicity": "",
        "is_match_plus": True,
        "latitud": 23.3223,
        "longitud": 55.82,
        "like_counter": 0,
        "superlike_counter": 0
    })
    assert response.status_code == 404, response.text

#def test_get_inexistent_user_profile_filter():
#    response = client.get("/user/1234/profiles/filter")
#    assert response.status_code == 404, response.text

#def test_get_inexistent_user_candidate():
#    response = client.get("/user/1234/match/nextcandidate")
#    assert response.status_code == 404, response.text