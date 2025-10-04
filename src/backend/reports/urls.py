"""
URLs for reports app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('pdf/<uuid:prediction_id>/', views.generate_pdf_report, name='generate_pdf_report'),
    path('share/', views.share_report, name='share_report'),
    path('shared/<uuid:share_token>/', views.view_shared_report, name='view_shared_report'),
    path('shared/', views.get_shared_reports, name='get_shared_reports'),
    path('shared/<uuid:share_id>/revoke/', views.revoke_shared_report, name='revoke_shared_report'),
]