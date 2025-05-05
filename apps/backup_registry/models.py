# apps/backup_registry/models.py

from django.db import models

class RegisteredDatabase(models.Model):
    """Representa um banco de dados cujo backup é gerenciado ou registrado."""
    name = models.CharField(
        max_length=255,
        unique=True, # Garante que não haja nomes duplicados
        db_index=True, # Cria um índice para buscas mais rápidas pelo nome
        help_text="Nome único do banco de dados registrado"
    )
    # Adicione outros campos se precisar no futuro, por exemplo:
    # description = models.TextField(blank=True, null=True)
    # is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True) # Data/Hora de criação do registro

    def __str__(self):
        # Como o objeto será representado como string (ex: no Admin)
        return self.name

    class Meta:
        # Opções do modelo
        verbose_name = "Banco de Dados Registrado"
        verbose_name_plural = "Bancos de Dados Registrados"
        ordering = ['name'] # Ordenar por nome por padrão