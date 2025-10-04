"""
URLs for predictions app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_mutations, name='analyze_mutations'),
    path('history/', views.get_prediction_history, name='prediction_history'),
    path('<uuid:prediction_id>/', views.get_prediction_details, name='prediction_details'),
    path('<uuid:prediction_id>/delete/', views.delete_prediction, name='delete_prediction'),
    path('dashboard/stats/', views.get_dashboard_stats, name='dashboard_stats'),
]