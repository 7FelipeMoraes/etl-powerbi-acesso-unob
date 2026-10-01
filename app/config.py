import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'unob_educbi')
DB_USER = os.getenv('DB_USER', 'bi_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_SCHEMA = os.getenv('DB_SCHEMA', 'powerbi_acesso')

# Captura do relatório exportado manualmente do Power BI
DOWNLOADS_DIR = os.getenv('DOWNLOADS_DIR') or os.path.join(
    os.path.expanduser('~'), 'Downloads'
)
DOWNLOAD_PATTERN = os.getenv('DOWNLOAD_PATTERN') or 'data*.xlsx'
DATA_DIR = os.getenv('DATA_DIR') or os.path.join(PROJECT_DIR, 'data')

DATABASE_URL = (
    f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)
