from .utils import *
from fastapi import status
from ..routers.admin import get_db, get_current_user
from ..Models import ToDo

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# test admin todo
def test_admin_read_all_authenticated(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"complete": False, "title": "aaa", "description": "aaa","id": 1, "priority": 5,  "owner_id": 1}]

# delete admin todo
def test_admin_delete_todo(test_todo):
    response = client.delete("/admin/todo/1")
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(ToDo).filter(ToDo.id == 1).first()
    assert model is None


# delete admin todo
def test_admin_delete_todo():
    response = client.delete("/admin/todo/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "No Todo Found"}
