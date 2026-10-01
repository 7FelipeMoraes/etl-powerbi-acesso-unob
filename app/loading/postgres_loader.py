import pandas as pd
from sqlalchemy import create_engine, text


def get_db_engine(database_url: str):
  """Cria a engine de conexão do SQLAlchemy."""
  return create_engine(database_url)


def load_dimension_usuarios(
    engine, schema: str, df_clean: pd.DataFrame
) -> pd.DataFrame:
  """Insere novos e-mails na d_usuario (UPSERT) e retorna a tabela mapeada com IDs."""
  print('[LOAD] Atualizando dimensão d_usuario...')

  # Extrair lista única de e-mails
  usuarios_unicos = (
      df_clean[['UniqueUser']]
      .drop_duplicates()
      .rename(columns={'UniqueUser': 'email_usuario'})
  )
  dados_usuarios = usuarios_unicos.to_dict(orient='records')

  with engine.connect() as conn:
    if dados_usuarios:
      query_upsert = text(f"""
                INSERT INTO {schema}.d_usuario (email_usuario)
                VALUES (:email_usuario)
                ON CONFLICT (email_usuario) DO NOTHING;
            """)
      conn.execute(query_upsert, dados_usuarios)
      conn.commit()

    # Recuperar mapeamento com os IDs atualizados apenas para a carga atual
    emails_carga = tuple(df_clean['UniqueUser'].dropna().unique())
    if emails_carga:
      query_select = text(
          f'SELECT id_usuario, email_usuario FROM {schema}.d_usuario '
          f'WHERE email_usuario IN :emails_carga'
      )
      df_usuarios_db = pd.read_sql(
          query_select, conn, params={'emails_carga': emails_carga}
      )
    else:
      df_usuarios_db = pd.DataFrame(columns=['id_usuario', 'email_usuario'])

  print(
      f'[LOAD] Dimensão d_usuario sincronizada ({len(df_usuarios_db)}'
      ' cadastrados no banco).'
  )
  return df_usuarios_db


def load_fact_acessos(
    engine, schema: str, df_clean: pd.DataFrame, df_usuarios_db: pd.DataFrame
):
  """Relaciona os dados com os IDs dos usuários e carrega na tabela fato f_acessos_powerbi."""
  print('[LOAD] Inserindo registros na tabela fato f_acessos_powerbi...')

  # Mapear email_usuario -> id_usuario (JOIN)
  df_fato = pd.merge(
      df_clean,
      df_usuarios_db,
      left_on='UniqueUser',
      right_on='email_usuario',
      how='left',
  )

  # Selecionar colunas finais
  df_fato_final = df_fato[
      ['id_usuario', 'Report opens', 'Total page views']
  ].copy()
  df_fato_final = df_fato_final.rename(
      columns={
          'Report opens': 'report_opens',
          'Total page views': 'total_page_views',
      }
  )

  # Timestamp da execução
  df_fato_final['data_atualizacao'] = pd.Timestamp.now()

  # Carga no banco
  df_fato_final.to_sql(
      'f_acessos_powerbi',
      con=engine,
      schema=schema,
      if_exists='append',
      index=False,
  )
  print(
      '[LOAD]'
      f' {len(df_fato_final)} registros inseridos na f_acessos_powerbi com'
      ' sucesso!'
  )