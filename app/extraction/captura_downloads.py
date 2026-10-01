import glob
import os
import shutil
from datetime import datetime


def _mover_sem_sobrescrever(origem: str, pasta_destino: str, prefixo: str) -> str:
  """Move o arquivo para a pasta com nome datado, sem sobrescrever existentes."""
  os.makedirs(pasta_destino, exist_ok=True)
  base = f'{prefixo}_{datetime.now():%Y%m%d_%H%M%S}'
  destino = os.path.join(pasta_destino, f'{base}.xlsx')
  sequencia = 1
  while os.path.exists(destino):
    destino = os.path.join(pasta_destino, f'{base}_{sequencia}.xlsx')
    sequencia += 1
  shutil.move(origem, destino)
  return destino


def capturar_relatorio(
    downloads_dir: str, data_dir: str, padrao: str = 'data*.xlsx'
) -> str:
  """Move o relatório exportado mais recente de Downloads para data/ e retorna o novo caminho."""
  candidatos = [
      f
      for f in glob.glob(os.path.join(downloads_dir, padrao))
      if not os.path.basename(f).startswith('~$')  # arquivo de bloqueio do Excel
  ]
  if not candidatos:
    raise FileNotFoundError(
        f'Nenhum arquivo "{padrao}" encontrado em {downloads_dir}. Exporte o'
        ' relatório do Power BI antes de executar o ETL.'
    )

  candidatos.sort(key=os.path.getmtime, reverse=True)
  origem, antigos = candidatos[0], candidatos[1:]

  # Exportações antigas saem de Downloads para não serem processadas depois
  for arquivo in antigos:
    destino = _mover_sem_sobrescrever(
        arquivo, os.path.join(data_dir, 'descartados'), 'descartado'
    )
    print(
        f'[EXTRACT] Aviso: exportação antiga {os.path.basename(arquivo)}'
        f' movida sem processar para {destino}'
    )

  destino = _mover_sem_sobrescrever(origem, data_dir, 'relatorio_acessos')
  print(f'[EXTRACT] Arquivo capturado: {os.path.basename(origem)} -> {destino}')
  return destino
