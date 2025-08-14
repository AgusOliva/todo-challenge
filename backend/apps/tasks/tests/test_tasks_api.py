import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apps.tasks.models import Task

@pytest.mark.django_db
def test_create_list_toggle_delete():
    user = User.objects.create_user("u", password="p")
    client = APIClient()
    # login JWT
    token = client.post(reverse("token_obtain_pair"), {"username":"u","password":"p"}, format="json").data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # create
    r = client.post("/api/tasks/", {"title":"A","description":"B"}, format="json")
    assert r.status_code == 201
    tid = r.data["id"]

    # list + filter
    r = client.get("/api/tasks/?q=A")
    assert r.status_code == 200 and r.data["results"][0]["title"] == "A"

    # toggle
    r = client.post(f"/api/tasks/{tid}/toggle/")
    assert r.status_code == 200 and r.data["completed"] is True

    # delete
    r = client.delete(f"/api/tasks/{tid}/")
    assert r.status_code == 204 and Task.objects.count() == 0