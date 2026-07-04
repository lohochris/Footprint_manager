from rest_framework.routers import DefaultRouter

from .views.evidence_viewset import EvidenceViewSet

router = DefaultRouter()
router.register(r"evidence", EvidenceViewSet, basename="evidence")

urlpatterns = router.urls
