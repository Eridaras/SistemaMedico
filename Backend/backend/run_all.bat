@echo off
echo ====================================
echo Iniciando todos los microservicios...
echo ====================================
echo.

REM Verificar que existe el archivo .env
if not exist .env (
    echo ERROR: No se encuentra el archivo .env
    echo Por favor copia .env.example a .env y configura tus credenciales
    pause
    exit /b 1
)

echo Iniciando servicios en segundo plano...
echo.

start "Auth Service (5001)" cmd /k "cd auth_service && python app.py"
timeout /t 2 /nobreak > nul

start "Inventario Service (5002)" cmd /k "cd inventario_service && python app.py"
timeout /t 2 /nobreak > nul

start "Historia Clinica Service (5003)" cmd /k "cd historia_clinica_service && python app.py"
timeout /t 2 /nobreak > nul

start "Facturacion Service (5004)" cmd /k "cd facturacion_service && python app.py"
timeout /t 2 /nobreak > nul

start "Citas Service (5005)" cmd /k "cd citas_service && python app.py"

echo.
echo ====================================
echo Todos los servicios han sido iniciados!
echo ====================================
echo.
echo Auth Service:           http://localhost:5001
echo Inventario Service:     http://localhost:5002
echo Historia Clinica:       http://localhost:5003
echo Facturacion Service:    http://localhost:5004
echo Citas Service:          http://localhost:5005
echo.
echo Para detener todos los servicios, cierra todas las ventanas de CMD
echo.
pause
