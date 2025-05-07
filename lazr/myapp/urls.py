from django.urls import path
from . import views

urlpatterns = [
    path("", views.my_view),

]# Compare this snippet from lazr/lazr/urls.py:
# from django.contrib import admin