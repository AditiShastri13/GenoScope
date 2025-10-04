"""
URLs for mutations app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_mutation_file, name='upload_mutation_file'),
    path('files/', views.get_user_files, name='get_user_files'),
    path('files/<uuid:file_id>/', views.get_file_details, name='get_file_details'),
    path('files/<uuid:file_id>/delete/', views.delete_file, name='delete_file'),
    path('files/<uuid:file_id>/mutations/', views.get_file_mutations, name='get_file_mutations'),
]