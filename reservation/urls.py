from django.urls import path
from .views import reservations_with_previous_reference

urlpatterns = [
    path("", reservations_with_previous_reference)
]