#!/bin/bash

echo "===================================="
echo "Iniciando todos los microservicios..."
echo "===================================="
echo ""

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo "ERROR: No se encuentra el archivo .env"
    echo "Por favor copia .env.example a .env y configura tus credenciales"
    exit 1
fi

echo "Iniciando servicios en segundo plano..."
echo ""

cd auth_service
python app.py &
AUTH_PID=$!
cd ..
sleep 2

cd inventario_service
python app.py &
INVENTARIO_PID=$!
cd ..
sleep 2

cd historia_clinica_service
python app.py &
HISTORIA_PID=$!
cd ..
sleep 2

cd facturacion_service
python app.py &
FACTURACION_PID=$!
cd ..
sleep 2

cd citas_service
python app.py &
CITAS_PID=$!
cd ..

echo ""
echo "===================================="
echo "Todos los servicios han sido iniciados!"
echo "===================================="
echo ""
echo "Auth Service:           http://localhost:5001 (PID: $AUTH_PID)"
echo "Inventario Service:     http://localhost:5002 (PID: $INVENTARIO_PID)"
echo "Historia Clinica:       http://localhost:5003 (PID: $HISTORIA_PID)"
echo "Facturacion Service:    http://localhost:5004 (PID: $FACTURACION_PID)"
echo "Citas Service:          http://localhost:5005 (PID: $CITAS_PID)"
echo ""
echo "Para detener todos los servicios, presiona Ctrl+C"
echo ""

# Trap Ctrl+C to kill all services
trap "kill $AUTH_PID $INVENTARIO_PID $HISTORIA_PID $FACTURACION_PID $CITAS_PID; exit" INT

# Wait for all background processes
wait
