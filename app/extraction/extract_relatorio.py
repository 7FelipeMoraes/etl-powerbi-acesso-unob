import os
import pandas as pd


def extract_excel_data(
    file_path: str, sheet_name: str = 'Export'
) -> pd.DataFrame:
  """Lê o arquivo Excel de métricas e retorna o DataFrame bruto."""
  if not os.path.exists(file_path):
    raise FileNotFoundError(
        f'Arquivo de origem não encontrado no caminho: {file_path}'
    )

  print(f'[EXTRACT] Lendo arquivo Excel: {file_path}')
  df_raw = pd.read_excel(file_path, sheet_name=sheet_name)
  print(f'[EXTRACT] Total de linhas lidas: {len(df_raw)}')
  return df_raw