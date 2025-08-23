from django.contrib import admin
from django.urls import path, include
# this is the main urls for project
urlpatterns = [
    path("", include("myapp.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
]
