from rest_framework import viewsets, mixins, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime, time

from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer
from . import services

# Create your views here.

def _parse_iso_datetime_or_date(value: str):
    """Acepta 'YYYY-MM-DDTHH:MM:SSZ' o 'YYYY-MM-DD'. Devuelve datetime naive."""
    if not value:
        return None
    dt = parse_datetime(value.replace("Z", "+00:00"))
    if dt:
        return dt.replace(tzinfo=None) if dt.tzinfo else dt
    try:
        d = datetime.strptime(value, "%Y-%m-%d").date()
        return datetime.combine(d, time.min)
    except ValueError:
        return None

class TaskViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title"]

    def get_queryset(self):
        qs = Task.objects.filter(owner=self.request.user)

        q = self.request.query_params.get("q")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        if date_from:
            dt_from = _parse_iso_datetime_or_date(date_from)
            if dt_from:
                qs = qs.filter(created_at__gte=timezone.make_aware(dt_from))

        if date_to:
            dt_to = _parse_iso_datetime_or_date(date_to)
            if dt_to:
                if dt_to.time() == time.min:
                    dt_to = datetime.combine(dt_to.date(), time.max)
                qs = qs.filter(created_at__lte=timezone.make_aware(dt_to))

        return qs

    def get_serializer_class(self):
        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        task = services.toggle_complete(owner=request.user, pk=pk)
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)