from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination


# Reusable base viewset that provides common DRF configuration
class BaseInvestigationViewSet(viewsets.GenericViewSet,
                              mixins.ListModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin):
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    # Throttling can be configured globally; placeholders left for future extension
    throttle_classes = []

    def get_service(self):
        """Return the associated service class instance if defined, else ``None``.
        Concrete viewsets may set ``service_class`` attribute.
        """
        service_class = getattr(self, "service_class", None)
        if service_class:
            return service_class()
        return None

    def perform_create(self, serializer):
        service = self.get_service()
        if service and hasattr(service, "create"):
            service.create(self.request.user, **serializer.validated_data)
        else:
            serializer.save()

    def perform_update(self, serializer):
        service = self.get_service()
        if service and hasattr(service, "update"):
            service.update(self.request.user, self.get_object(), **serializer.validated_data)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        service = self.get_service()
        if service and hasattr(service, "delete"):
            service.delete(self.request.user, instance)
        else:
            instance.delete()
