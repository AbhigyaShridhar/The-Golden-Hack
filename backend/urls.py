from django.urls import path

from . import views

app_name = "backend"

urlpatterns = [
    path('', views.index, name="index"),
]
