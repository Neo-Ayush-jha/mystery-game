from django.urls import path
from .views import *

urlpatterns = [
    path('generate-case/', generate_case, name='generate_case'),
    path('interrogate-suspect/<int:suspect_id>/', interrogate_suspect, name='interrogate_suspect'),
    path("case-details/<int:case_id>/", case_details, name="case_details"),
]
