from rest_framework import permissions

class IntegrationManagePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'tenant_id', None) is not None

class WebhookReceiverPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow any, as webhook payload will be verified by the provider itself
        return True
