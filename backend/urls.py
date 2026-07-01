from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include investigation API routes
    path('api/', include('investigations.api.router')),
    # Existing app routes can be included here
]
