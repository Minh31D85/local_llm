from django.urls import path
from .views import generate_code, index, history, del_history_entry

urlpatterns = [
    path("", index),
    path("generate/", generate_code),
    path("history/", history),
    path("history/<int:entry_id>/", del_history_entry)
]