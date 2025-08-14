from rest_framework.exceptions import NotFound
from django.db import transaction
from .models import Task

@transaction.atomic
def create_task(*, owner, title, description=""):
    return Task.objects.create(owner=owner, title=title, description=description)

@transaction.atomic
def delete_task(*, owner, pk):
    try:
        Task.objects.filter(owner=owner, pk=pk).delete()
    except Task.DoesNotExist:
        raise NotFound("Task not found")
    
@transaction.atomic
def toggle_complete(*, owner, pk):
    try:
        t = Task.objects.get(owner=owner, pk=pk)
    except Task.DoesNotExist:
        raise NotFound("Task not found")
    t.completed = not t.completed
    t.save(update_fields=["completed"])
    return t