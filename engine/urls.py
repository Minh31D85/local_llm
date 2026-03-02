from django.urls import path
from .views import generate_code, index

urlpatterns = [
    path("", index),
    path("generate/", generate_code)
]