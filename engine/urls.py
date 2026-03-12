from django.urls import path
from .views import generate_code, index, history, del_history_entry

urlpatterns = [
    path("", index),
    path("api/generate/", generate_code),
    path("api/history/", history),
    path("api/history/<int:entry_id>/", del_history_entry)
]