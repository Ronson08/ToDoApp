from .utils import *
from ..routers.auth import authenticate_user, get_db, access_token, SECRET_KEY, get_current_user, ALGORITHM
from jose import jwt
from datetime import timedelta
from fastapi import status, HTTPException

app.dependency_overrides[get_db] = override_get_db

def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username, 'aaa', db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_exit_user = authenticate_user("abc", 'aaa', db)
    assert non_exit_user is False

    wrong_pass = authenticate_user(test_user.username, 'abc', db)
    assert wrong_pass is False

def test_access_token():
    username = "test_user"
    user_id = 1
    role = "user"
    expire_delta = timedelta(days=1)

    token = access_token(username, user_id, role, expire_delta)

    decode_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
    
    assert decode_token['sub'] == username
    assert decode_token['id'] == user_id
    assert decode_token['role'] == role

@pytest.mark.asyncio
async def test_get_current_user():
    encode = {'sub': 'aaa', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {'username': 'aaa', 'id': 1, 'user_role': 'admin'}

@pytest.mark.asyncio
async def test_get_current_user_missing():
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)
        
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Couldnot Validate the User"
