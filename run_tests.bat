@echo off
echo ==================================
echo Ejecutando tests de todos los servicios...
echo ==================================

set failed=0

echo.
echo [1/5] Testing Auth Service...
cd auth_service
if exist tests (
    pytest tests/ -v
    if %ERRORLEVEL% NEQ 0 (
        echo X Auth Service tests failed
        set failed=1
    ) else (
        echo + Auth Service tests passed
    )
) else (
    echo ! No tests directory found
)
cd ..

echo.
echo [2/5] Testing Inventario Service...
cd inventario_service
if exist tests (
    pytest tests/ -v
    if %ERRORLEVEL% NEQ 0 (
        echo X Inventario Service tests failed
        set failed=1
    ) else (
        echo + Inventario Service tests passed
    )
) else (
    echo ! No tests directory found
)
cd ..

echo.
echo [3/5] Testing Historia Clinica Service...
cd historia_clinica_service
if exist tests (
    pytest tests/ -v
    if %ERRORLEVEL% NEQ 0 (
        echo X Historia Clinica Service tests failed
        set failed=1
    ) else (
        echo + Historia Clinica Service tests passed
    )
) else (
    echo ! No tests directory found
)
cd ..

echo.
echo [4/5] Testing Facturacion Service...
cd facturacion_service
if exist tests (
    pytest tests/ -v
    if %ERRORLEVEL% NEQ 0 (
        echo X Facturacion Service tests failed
        set failed=1
    ) else (
        echo + Facturacion Service tests passed
    )
) else (
    echo ! No tests directory found
)
cd ..

echo.
echo [5/5] Testing Citas Service...
cd citas_service
if exist tests (
    pytest tests/ -v
    if %ERRORLEVEL% NEQ 0 (
        echo X Citas Service tests failed
        set failed=1
    ) else (
        echo + Citas Service tests passed
    )
) else (
    echo ! No tests directory found
)
cd ..

echo.
echo ==================================
if %failed% EQU 0 (
    echo + Todos los tests pasaron exitosamente!
) else (
    echo X Algunos tests fallaron
    exit /b 1
)
echo ==================================
pause
