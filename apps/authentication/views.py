# apps/authentication/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required # Para proteger a view
import boto3
from botocore.exceptions import ClientError # Para tratar erros do Boto3
import os # Para pegar variáveis de ambiente se necessário (opcional)

# (Mantenha outras views que você possa ter aqui)

@login_required # Garante que só usuários logados acessem esta view
def list_backup_files(request):
    """
    View para listar arquivos do bucket S3 no prefixo 'diario/'.
    """
    s3_files = []
    error_message = None
    bucket_name = 'mybackuprdscorebank' # Nome do seu bucket
    prefix = 'diario/' # Pasta/Prefixo dentro do bucket

    try:
        # Inicializa o cliente S3. Como estamos na EC2 com uma Role,
        # Boto3 usará as credenciais da Role automaticamente.
        s3_client = boto3.client('s3')

        # Lista os objetos no bucket/prefixo especificado
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        # Verifica se a chave 'Contents' existe na resposta (indica que há objetos)
        if 'Contents' in response:
            # Monta a lista de arquivos, opcionalmente removendo o prefixo do nome
            # e ignorando o próprio objeto do prefixo (se listado)
            for obj in response['Contents']:
                # Pega a chave (nome completo do arquivo no S3)
                file_key = obj['Key']
                # Só adiciona à lista se não for o próprio diretório/prefixo
                if file_key != prefix:
                    # Opcional: remover o prefixo para exibição mais limpa
                    # display_name = file_key.replace(prefix, '', 1)
                    # s3_files.append(display_name)

                    # Ou exibir o caminho completo
                    s3_files.append(file_key)
        else:
            # Nenhum arquivo encontrado no prefixo
            s3_files = [] # Garante que a lista está vazia

        # Lógica de paginação seria necessária aqui se houvesse muitos arquivos
        # Ex: verificar response['IsTruncated'] e usar response['NextContinuationToken']

    except ClientError as e:
        # Captura erros específicos do Boto3/AWS (ex: acesso negado)
        error_message = f"Erro ao acessar o S3: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
        # Você pode querer logar o erro completo também: logging.error(e)
    except Exception as e:
        # Captura outros erros inesperados
        error_message = f"Ocorreu um erro inesperado: {e}"
        # logging.error(e)

    context = {
        's3_files': s3_files,
        'error_message': error_message,
        'bucket_name': bucket_name,
        'prefix': prefix,
    }
    return render(request, 'authentication/list_s3_files.html', context)