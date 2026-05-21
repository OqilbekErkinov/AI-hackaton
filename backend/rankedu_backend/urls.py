from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from core.views import admin_ai_chat_view, landing_view
from unfold.sites import UnfoldAdminSite

from .admin_site import admin_site

urlpatterns = [
    path("", landing_view, name="landing"),
    path("api/", include("core.urls")),
    path('admin/ai-assistant/', admin_ai_chat_view),
    path("admin/", admin_site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


