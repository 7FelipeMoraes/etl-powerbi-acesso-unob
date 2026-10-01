import argparse
import sys
from app import config
from app.extraction.captura_downloads import capturar_relatorio
from app.extraction.extract_relatorio import extract_excel_data
from app.loading.postgres_loader import (
    get_db_engine,
    load_dimension_usuarios,
    load_fact_acessos,
)
from app.transform.relatorio_trat import transform_metrics_data


def run_pipeline(arquivo: str | None = None):
  print('=== INICIANDO PIPELINE ETL DE ACESSOS POWER BI ===')

  try:
    # 1. Extração: captura de Downloads (ou reprocessa um arquivo informado)
    file_path = arquivo or capturar_relatorio(
        config.DOWNLOADS_DIR, config.DATA_DIR, config.DOWNLOAD_PATTERN
    )
    df_raw = extract_excel_data(file_path=file_path, sheet_name='Export')

    # 2. Transformação
    df_clean = transform_metrics_data(df_raw)

    # 3. Carga
    engine = get_db_engine(config.DATABASE_URL)
    df_usuarios_db = load_dimension_usuarios(engine, config.DB_SCHEMA, df_clean)
    load_fact_acessos(engine, config.DB_SCHEMA, df_clean, df_usuarios_db)

    print('\n === PIPELINE FINALIZADO COM SUCESSO! ===')

  except Exception as e:
    print(f'\n[ERRO CRÍTICO] Falha na execução do ETL: {e}', file=sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='ETL de acessos Power BI')
  parser.add_argument(
      '--arquivo',
      help='Reprocessa um arquivo já salvo (ex.: data/relatorio_acessos_...xlsx)'
      ' em vez de capturar de Downloads.',
  )
  args = parser.parse_args()
  run_pipeline(args.arquivo)
