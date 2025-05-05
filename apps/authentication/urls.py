# apps/authentication/urls.py

from django.urls import path
from . import views # Importa as views da app atual

# Define um namespace para evitar conflitos de nomes de URL (opcional, mas bom)
app_name = 'authentication'

urlpatterns = [
    # Adicione outras URLs da app aqui se tiver
    # ...

    # URL para a nossa nova view de listar arquivos S3
    path('backups/diario/', views.list_backup_files, name='list_backup_files'),
]