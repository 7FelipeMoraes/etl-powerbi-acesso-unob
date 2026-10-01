@echo off

:: ============================================================================
:: SCRIPT DE ORQUESTRACAO DO ETL DE ACESSOS POWER BI
:: Compatível com Agendador de Tarefas do Windows (Task Scheduler)
:: ============================================================================

TITLE ETL Power BI Acessos Executer

:: 1. Definir diretorios do projeto e logs de forma dinamica
SET "PROJECT_DIR=%~dp0"
IF "%PROJECT_DIR:~-1%"=="\" SET "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
SET "LOG_DIR=%PROJECT_DIR%\logs"
SET "LOG_FILE=%LOG_DIR%\etl_execution.log"


:: 2. Criar diretório de logs se não existir 
IF NOT EXIST "%LOG_DIR%" (
    MKDIR "%LOG_DIR%"
)


:: 3. Navegar até a raiz do projeto
CD /D "%PROJECT_DIR%"

:: 4. Registrar início no log
ECHO ============================================================================ >> "%LOG_FILE%"
ECHO [INFO] Iniciando execução do ETL: %DATE% as %TIME% >> "%LOG_FILE%"

:: 5. Executar o script Python redirecionando saídas padrão e erros para o log
"%PROJECT_DIR%\.venv\Scripts\python.exe" main.py >> "%LOG_FILE%" 2>&1

:: 6. Tratar o código de retorno (Exit Code)
IF %ERRORLEVEL% EQU 0 (
    ECHO [SUCESSO] ETL executado com sucesso em %DATE% as %TIME% >> "%LOG_FILE%"
    EXIT /B 0
) ELSE (
    ECHO [ERRO] Falha na execução do ETL ^(Código: %ERRORLEVEL%^) em %DATE% as %TIME% >> "%LOG_FILE%"
    EXIT /B %ERRORLEVEL%
)