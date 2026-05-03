"""
civic_project/urls.py — Root URL dispatcher
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Django admin (superuser only)
    path('django-admin/', admin.site.urls),

    # Redirect root → login
    path('', RedirectView.as_view(url='/users/login/', permanent=False)),

    # App URLs
    path('users/', include('users.urls', namespace='users')),
    path('complaints/', include('complaints.urls', namespace='complaints')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
