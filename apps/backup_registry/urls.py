# apps/backup_registry/urls.py
from django.urls import path
from . import views

app_name = 'backup_registry'

urlpatterns = [
    path('status/', views.backup_status_table, name='backup_status'),
]