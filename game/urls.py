from django.urls import path
from .views import *

urlpatterns = [
    path("total_cases/", total_cases, name="total_cases"),
    path('generate-case/', generate_case, name='generate_case'),
    path("solve_case/<int:case_id>/", solve_case, name="solve_case"),
    path("case-details/<int:case_id>/", case_details, name="case_details"),
    path('interrogate-suspect/<int:suspect_id>/', interrogate_suspect, name='interrogate_suspect'),
]
