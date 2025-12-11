#!/bin/bash

echo "===================================="
echo "Instalando dependencias..."
echo "===================================="

echo ""
echo "[1/5] Instalando Auth Service..."
cd auth_service
pip install -r requirements.txt
cd ..

echo ""
echo "[2/5] Instalando Inventario Service..."
cd inventario_service
pip install -r requirements.txt
cd ..

echo ""
echo "[3/5] Instalando Historia Clinica Service..."
cd historia_clinica_service
pip install -r requirements.txt
cd ..

echo ""
echo "[4/5] Instalando Facturacion Service..."
cd facturacion_service
pip install -r requirements.txt
cd ..

echo ""
echo "[5/5] Instalando Citas Service..."
cd citas_service
pip install -r requirements.txt
cd ..

echo ""
echo "===================================="
echo "Instalacion completada!"
echo "===================================="
echo ""
echo "Para ejecutar los servicios, usa: ./run_all.sh"
echo ""
