from .utils import *
from ..routers.users import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# test user data
def test_return_user(test_user):
    response = client.get('/user')
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data['username'] == "aaa"
    assert response_data['email'] == "aaa"
    assert response_data['first_name'] == "aaa"
    assert response_data['last_name'] == "aaa"
    assert response_data['is_active'] == True
    assert response_data['role'] == "admin"
    assert response_data['phone_number'] == "12345"
    assert response_data['id'] == 1
    
# change user password
def test_change_password(test_user):
    response = client.put("/user/password_change", json={
  "password": "aaa",
  "new_password": "aaaa"
})
    assert response.status_code == status.HTTP_204_NO_CONTENT

# change user password fail
def test_change_password_invalid_password(test_user):
    response = client.put("/user/password_change", json={
  "password": "ccc",
  "new_password": "aaaa"
})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Error on password change"}

#change user phone number
def test_change_user_phone_number(test_user):
    response = client.put("/user/phone_number?new_phone_number=123445")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    