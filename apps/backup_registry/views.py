# apps/backup_registry/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now # Para pegar a data atual com timezone
import datetime
import re # Para expressões regulares (parsing de nome de arquivo)
import boto3
from botocore.exceptions import ClientError
from .models import RegisteredDatabase # Importa o modelo dos bancos registrados

@login_required
def backup_status_table(request):
    """
    Busca backups no S3 e compara com bancos registrados para exibir
    uma tabela de status dos últimos 15 dias.
    """
    registered_databases = list(RegisteredDatabase.objects.values_list('name', flat=True).order_by('name'))
    error_message = None
    s3_backups_found = {} # Dicionário: {'DB_NAME': {date(YYYY, MM, DD), ...}}

    bucket_name = 'mybackuprdscorebank'
    prefix = 'diario/'

    # 1. Listar e processar arquivos do S3
    try:
        s3_client = boto3.client('s3')
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

        # Regex para extrair NOME_DB e DATA do nome do arquivo
        # Ex: diario/AB_CADASTROPOSITIVO-2025-04-28-050706.bak
        # Grupo 1: DB_NAME
        # Grupo 2: YYYY-MM-DD
        filename_pattern = re.compile(r'^' + prefix + r'([A-Z0-9_]+)-(\d{4}-\d{2}-\d{2})-\d{6}\.bak$')

        for page in pages: # Itera sobre páginas de resultados (caso > 1000 arquivos)
            if 'Contents' in page:
                for obj in page['Contents']:
                    file_key = obj['Key']
                    match = filename_pattern.match(file_key)
                    if match:
                        db_name = match.group(1)
                        date_str = match.group(2)
                        try:
                            backup_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

                            if db_name not in s3_backups_found:
                                s3_backups_found[db_name] = set()
                            s3_backups_found[db_name].add(backup_date)
                        except ValueError:
                            # Ignora arquivos com formato de data inválido no nome
                            pass # Ou logar um aviso

    except ClientError as e:
        error_message = f"Erro ao listar/processar arquivos do S3: {e.response['Error']['Code']}"
    except Exception as e:
        error_message = f"Ocorreu um erro inesperado no processamento S3: {e}"

    # 2. Gerar as datas dos últimos 15 dias
    today = now().date() # Pega a data atual
    header_dates_obj = [today - datetime.timedelta(days=i) for i in range(15)] # Lista de objetos date
    header_dates_str = [d.strftime('%d/%m/%Y') for d in header_dates_obj] # Lista de strings formatadas

    # 3. Montar os dados da tabela
    table_data = []
    if not error_message: # Só monta a tabela se não houve erro no S3
        for db_name in registered_databases:
            backup_status_list = []
            # Pega o conjunto de datas para este DB, ou um conjunto vazio se não achou backups
            db_backup_dates = s3_backups_found.get(db_name, set())

            for target_date in header_dates_obj:
                if target_date in db_backup_dates:
                    # Encontrou backup para esta data
                    backup_status_list.append(target_date.strftime('%d/%m/%Y'))
                else:
                    # Não encontrou backup
                    backup_status_list.append("SEM BACKUP")

            table_data.append({
                'db_name': db_name,
                'backup_status': backup_status_list
            })

    context = {
        'header_dates': header_dates_str, # Datas para o cabeçalho da tabela
        'table_data': table_data,         # Dados das linhas da tabela
        'error_message': error_message,   # Mensagem de erro (se houver)
    }
    return render(request, 'backup_registry/backup_status.html', context)