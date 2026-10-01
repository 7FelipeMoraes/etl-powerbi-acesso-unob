import pandas as pd


def transform_metrics_data(df: pd.DataFrame) -> pd.DataFrame:
  """Aplica regras de limpeza, padronização e tipos nos dados."""
  print('[TRANSFORM] Limpando e tratando os dados...')

  df_clean = df.copy()

  # 1. Limpar espaços nos nomes das colunas
  df_clean.columns = df_clean.columns.str.strip()

  # 2. Validar coluna de usuário
  if 'UniqueUser' not in df_clean.columns:
    raise KeyError("A coluna obrigatória 'UniqueUser' não existe no arquivo.")

  # 3. Remover linhas sem usuário e padronizar e-mails (minúsculo e sem espaços)
  df_clean = df_clean.dropna(subset=['UniqueUser'])
  df_clean['UniqueUser'] = (
      df_clean['UniqueUser'].astype(str).str.strip().str.lower()
  )

  # 4. Manter só e-mails válidos (descarta o rodapé "Filtros aplicados" do export)
  email_valido = df_clean['UniqueUser'].str.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+')
  descartadas = int((~email_valido).sum())
  if descartadas:
    print(f'[TRANSFORM] {descartadas} linha(s) sem e-mail válido descartada(s).')
  df_clean = df_clean[email_valido]

  # 5. Tratar colunas numéricas
  for col in ['Report opens', 'Total page views']:
    if col not in df_clean.columns:
      df_clean[col] = 0
    df_clean[col] = df_clean[col].fillna(0).astype(int)

  print(f'[TRANSFORM] Registros válidos prontos: {len(df_clean)}')
  return df_clean