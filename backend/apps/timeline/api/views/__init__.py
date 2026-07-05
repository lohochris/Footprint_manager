from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ....models import EventCluster, Timeline, TimelineEvent, TimelineSnapshot
from ..serializers import (
    EventClusterSerializer,
    TimelineEventSerializer,
    TimelineSerializer,
    TimelineSnapshotSerializer,
)


class TimelineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Timeline.objects.all()
    serializer_class = TimelineSerializer

    def get_queryset(self):
        return super().get_queryset()

    @action(detail=True, methods=["get"])
    def playback(self, request, pk=None):
        timeline = self.get_object()
        # Integration with PlaybackService goes here
        # Return reconstructed state at requested timestamp
        return Response({"status": "playback_generated"})


class TimelineEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TimelineEvent.objects.all()
    serializer_class = TimelineEventSerializer

    def get_queryset(self):
        # Filtering logic for timestamp, resource, investigation
        return super().get_queryset()


class EventClusterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventCluster.objects.all()
    serializer_class = EventClusterSerializer


class TimelineSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TimelineSnapshot.objects.all()
    serializer_class = TimelineSnapshotSerializer
