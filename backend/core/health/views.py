"""Health check endpoints for Footprint Manager."""

import structlog
from django.db import connection
from django.http import JsonResponse
from django.views import View
from redis.exceptions import RedisError

logger = structlog.get_logger(__name__)


class HealthCheckView(View):
    """Basic liveness probe."""

    def get(self, _request: object) -> JsonResponse:
        """Return a healthy response when the Django process is reachable."""
        return JsonResponse({"status": "healthy", "service": "footprint-manager"})


class ReadinessCheckView(View):
    """Readiness probe verifying database and cache connectivity."""

    def get(self, _request: object) -> JsonResponse:
        """Return dependency readiness details for orchestration probes."""
        checks: dict[str, str] = {}
        overall_status = "ready"

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            checks["database"] = "ok"
        except Exception as exc:
            logger.error("readiness_database_failed", error=str(exc))
            checks["database"] = "failed"
            overall_status = "not_ready"

        try:
            from django.core.cache import cache

            cache.set("_health_check", "1", timeout=5)
            if cache.get("_health_check") == "1":
                checks["cache"] = "ok"
            else:
                checks["cache"] = "failed"
                overall_status = "not_ready"
        except RedisError as exc:
            logger.error("readiness_cache_redis_failed", error=str(exc))
            checks["cache"] = "failed"
            overall_status = "not_ready"
        except Exception as exc:
            logger.error("readiness_cache_failed", error=str(exc))
            checks["cache"] = "failed"
            overall_status = "not_ready"

        status_code = 200 if overall_status == "ready" else 503
        return JsonResponse(
            {"status": overall_status, "checks": checks},
            status=status_code,
        )
