# **Documentação da Implementação da Arquitetura Modular ETL**

Esta reestruturação organiza o projeto no padrão profissional de Engenharia de Dados (arquitetura modular ETL), separando as responsabilidades de extração, transformação, carga e gerenciamento de credenciais.

## ---

**📂 Estrutura de Pastas do Projeto**

Organize a sua pasta raiz etl\_acessos\_bi com a seguinte árvore de diretórios:  
etl\_acessos\_bi/  
│  
├── .env                        \# Credenciais e configurações (não vai para o Git)  
├── .gitignore                  \# Arquivos ignorados pelo Git  
├── requirements.txt            \# Dependências do projeto  
├── main.py                     \# Orquestrador do ETL (Ponto de entrada)  
│  
└── app/  
    ├── \_\_init\_\_.py             \# Módulo Python da aplicação  
    ├── config.py               \# Leitor de variáveis de ambiente do .env  
    │  
    ├── extraction/             \# Módulo de Extração (E)  
    │   ├── \_\_init\_\_.py  
    │   └── excel\_extractor.py  
    │  
    ├── transformation/         \# Módulo de Transformação (T)  
    │   ├── \_\_init\_\_.py  
    │   └── metrics\_transformer.py  
    │  
    └── loading/                \# Módulo de Carga (L)  
        ├── \_\_init\_\_.py  
        └── postgres\_loader.py

## ---

**📄 Códigos-Fonte de Cada Arquivo**

### **1\. .env (Raiz do projeto)**

\# Configurações do Banco de Dados  
DB\_HOST=
DB\_PORT=5432  
DB\_NAME=unob\_educbi  
DB\_USER=  
DB\_PASSWORD=  
DB\_SCHEMA=powerbi\_acesso

\# Configurações de Origem de Dados  
EXCEL\_FILE\_PATH=C:\\Users\\luiz.moraes\\Downloads\\data.xlsx

### **2\. .gitignore (Raiz do projeto)**

.env  
\_\_pycache\_\_/  
\*.pyc  
.venv/  
env/  
logs/

### **3\. requirements.txt (Raiz do projeto)**

pandas  
sqlalchemy  
psycopg2-binary  
openpyxl  
python-dotenv

### ---

**4\. app/config.py**

import os  
from dotenv import load\_dotenv

\# Carrega variáveis do arquivo .env  
load\_dotenv()

DB\_HOST \= os.getenv('DB\_HOST', ' ')  
DB\_PORT \= os.getenv('DB\_PORT', '5432')  
DB\_NAME \= os.getenv('DB\_NAME', 'unob\_educbi')  
DB\_USER \= os.getenv('DB\_USER', ' ')  
DB\_PASSWORD \= os.getenv('DB\_PASSWORD', '')  
DB\_SCHEMA \= os.getenv('DB\_SCHEMA', 'powerbi\_acesso')  
EXCEL\_FILE\_PATH \= os.getenv('EXCEL\_FILE\_PATH', '')

DATABASE\_URL \= (  
    f'postgresql://{DB\_USER}:{DB\_PASSWORD}@{DB\_HOST}:{DB\_PORT}/{DB\_NAME}'  
)

### ---

**5\. app/extraction/excel\_extractor.py**

import os  
import pandas as pd

def extract\_excel\_data(  
    file\_path: str, sheet\_name: str \= 'Export'  
) \-\> pd.DataFrame:  
  """Lê o arquivo Excel de métricas e retorna o DataFrame bruto."""  
  if not os.path.exists(file\_path):  
    raise FileNotFoundError(  
        f'Arquivo de origem não encontrado no caminho: {file\_path}'  
    )

  print(f'\[EXTRACT\] Lendo arquivo Excel: {file\_path}')  
  df\_raw \= pd.read\_excel(file\_path, sheet\_name=sheet\_name)  
  print(f'\[EXTRACT\] Total de linhas lidas: {len(df\_raw)}')  
  return df\_raw

### ---

**6\. app/transformation/metrics\_transformer.py**

import pandas as pd

def transform\_metrics\_data(df: pd.DataFrame) \-\> pd.DataFrame:  
  """Aplica regras de limpeza, padronização e tipos nos dados."""  
  print('🧹 \[TRANSFORM\] Limpando e tratando os dados...')

  df\_clean \= df.copy()

  \# 1\. Limpar espaços nos nomes das colunas  
  df\_clean.columns \= df\_clean.columns.str.strip()

  \# 2\. Validar coluna de usuário  
  if 'UniqueUser' not in df\_clean.columns:  
    raise KeyError("A coluna obrigatória 'UniqueUser' não existe no arquivo.")

  \# 3\. Remover linhas sem usuário e padronizar e-mails (minúsculo e sem espaços)  
  df\_clean \= df\_clean.dropna(subset=\['UniqueUser'\])  
  df\_clean\['UniqueUser'\] \= (  
      df\_clean\['UniqueUser'\].astype(str).str.strip().str.lower()  
  )

  \# 4\. Tratar colunas numéricas  
  df\_clean\['Report opens'\] \= (  
      df\_clean.get('Report opens', 0).fillna(0).astype(int)  
  )  
  df\_clean\['Total page views'\] \= (  
      df\_clean.get('Total page views', 0).fillna(0).astype(int)  
  )

  print(f'\[TRANSFORM\] Registros válidos prontos: {len(df\_clean)}')  
  return df\_clean

### ---

**7\. app/loading/postgres\_loader.py**

import pandas as pd  
from sqlalchemy import create\_engine, text

def get\_db\_engine(database\_url: str):  
  """Cria a engine de conexão do SQLAlchemy."""  
  return create\_engine(database\_url)

def load\_dimension\_usuarios(  
    engine, schema: str, df\_clean: pd.DataFrame  
) \-\> pd.DataFrame:  
  """Insere novos e-mails na d\_usuario (UPSERT) e retorna a tabela mapeada com IDs."""  
  print('\[LOAD\] Atualizando dimensão d\_usuario...')

  \# Extrair lista única de e-mails  
  usuarios\_unicos \= (  
      df\_clean\[\['UniqueUser'\]\]  
      .drop\_duplicates()  
      .rename(columns={'UniqueUser': 'email\_usuario'})  
  )  
  dados\_usuarios \= usuarios\_unicos.to\_dict(orient='records')

  with engine.connect() as conn:  
    if dados\_usuarios:  
      query\_upsert \= text(f"""  
                INSERT INTO {schema}.d\_usuario (email\_usuario)  
                VALUES (:email\_usuario)  
                ON CONFLICT (email\_usuario) DO NOTHING;  
            """)  
      conn.execute(query\_upsert, dados\_usuarios)  
      conn.commit()

    \# Recuperar mapeamento com os IDs atualizados  
    df\_usuarios\_db \= pd.read\_sql(  
        f'SELECT id\_usuario, email\_usuario FROM {schema}.d\_usuario', conn  
    )

  print(  
      f'\[LOAD\] Dimensão d\_usuario sincronizada ({len(df\_usuarios\_db)}'  
      ' cadastrados no banco).'  
  )  
  return df\_usuarios\_db

def load\_fact\_acessos(  
    engine, schema: str, df\_clean: pd.DataFrame, df\_usuarios\_db: pd.DataFrame  
):  
  """Relaciona os dados com os IDs dos usuários e carrega na tabela fato f\_acessos\_powerbi."""  
  print('\[LOAD\] Inserindo registros na tabela fato f\_acessos\_powerbi...')

  \# Mapear email\_usuario \-\> id\_usuario (JOIN)  
  df\_fato \= pd.merge(  
      df\_clean,  
      df\_usuarios\_db,  
      left\_on='UniqueUser',  
      right\_on='email\_usuario',  
      how='left',  
  )

  \# Selecionar colunas finais  
  df\_fato\_final \= df\_fato\[  
      \['id\_usuario', 'Report opens', 'Total page views'\]  
  \].copy()  
  df\_fato\_final \= df\_fato\_final.rename(  
      columns={  
          'Report opens': 'report\_opens',  
          'Total page views': 'total\_page\_views',  
      }  
  )

  \# Timestamp da execução  
  df\_fato\_final\['data\_atualizacao'\] \= pd.Timestamp.now()

  \# Carga no banco  
  df\_fato\_final.to\_sql(  
      'f\_acessos\_powerbi',  
      con=engine,  
      schema=schema,  
      if\_exists='append',  
      index=False,  
  )  
  print(  
      '\[LOAD\]'  
      f' {len(df\_fato\_final)} registros inseridos na f\_acessos\_powerbi com'  
      ' sucesso\!'  
  )

### ---

**8\. main.py (Orquestrador)**

import sys  
from app.config import DATABASE\_URL, DB\_SCHEMA, EXCEL\_FILE\_PATH  
from app.extraction.excel\_extractor import extract\_excel\_data  
from app.loading.postgres\_loader import (  
    get\_db\_engine,  
    load\_dimension\_usuarios,  
    load\_fact\_acessos,  
)  
from app.transformation.metrics\_transformer import transform\_metrics\_data

def run\_pipeline():  
  print('\=== INICIANDO PIPELINE ETL DE ACESSOS POWER BI \===')

  try:  
    \# 1\. Extração  
    df\_raw \= extract\_excel\_data(file\_path=EXCEL\_FILE\_PATH, sheet\_name='Export')

    \# 2\. Transformação  
    df\_clean \= transform\_metrics\_data(df\_raw)

    \# 3\. Carga  
    engine \= get\_db\_engine(DATABASE\_URL)  
    df\_usuarios\_db \= load\_dimension\_usuarios(engine, DB\_SCHEMA, df\_clean)  
    load\_fact\_acessos(engine, DB\_SCHEMA, df\_clean, df\_usuarios\_db)

    print('\\n\=== PIPELINE FINALIZADO COM SUCESSO\! \===')

  except Exception as e:  
    print(f'\\n\[ERRO CRÍTICO\] Falha na execução do ETL: {e}', file=sys.stderr)  
    sys.exit(1)

if \_\_name\_\_ \== '\_\_main\_\_':  
  run\_pipeline()

## ---

**Como Executar**

> 1. Certifique-se de criar os arquivos de inicialização vazios \_\_init\_\_.py dentro das pastas app, extraction, transformation e loading.  
> 2. Instale os requisitos:  
>    pip install \-r requirements.txt  
> 3. Execute o orquestrador a partir da raiz do projeto:  
>    python main.py
## ---

**📥 Extração Semiautomática (captura de Downloads)**

O relatório é exportado manualmente do Power BI e o ETL cuida do restante:

Exportação manual (Power BI → Exportar dados → .xlsx) → Downloads/data.xlsx → captura\_downloads (move para data/relatorio\_acessos\_AAAAMMDD\_HHMMSS.xlsx) → extract\_excel\_data → transform\_metrics\_data → carga no Postgres

* **app/extraction/captura\_downloads.py**: procura em Downloads o arquivo mais recente que corresponda a DOWNLOAD\_PATTERN, move-o para data/ com data e hora no nome e devolve o caminho para a leitura. Exportações mais antigas com o mesmo padrão são movidas, sem processar, para data/descartados/ (com aviso no log), para não serem carregadas em execuções futuras. Nomes repetidos no mesmo segundo recebem sufixo (\_1, \_2...) e nunca são sobrescritos.
* Como o arquivo é **movido**, a mesma exportação não é processada duas vezes. Se não houver arquivo em Downloads, o ETL falha com mensagem orientando a exportar o relatório.
* A estrutura das tabelas no banco não muda.

### **Variáveis no .env**

| Variável | Descrição |
| :---- | :---- |
| DOWNLOADS\_DIR | Pasta onde o navegador salva a exportação (padrão: %USERPROFILE%\Downloads) |
| DOWNLOAD\_PATTERN | Padrão do nome do arquivo exportado (padrão: data\*.xlsx, cobre "data.xlsx" e "data (1).xlsx") |
| DATA\_DIR | Pasta de destino dos arquivos capturados (padrão: data/ do projeto) |

### **Como executar**

1. No Power BI, abra o visual → Mais opções (…) → Exportar dados → .xlsx.
2. Execute executar\_etl.bat (ou python main.py).
3. Para reprocessar um arquivo já capturado: python main.py --arquivo data\relatorio\_acessos\_AAAAMMDD\_HHMMSS.xlsx
