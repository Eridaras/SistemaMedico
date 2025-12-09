#!/bin/bash

echo "=================================="
echo "Ejecutando tests de todos los servicios..."
echo "=================================="

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

failed=0

# Verificar si pytest está instalado
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}pytest no está instalado. Instalando...${NC}"
    pip install pytest pytest-flask
fi

# Auth Service
echo ""
echo -e "${YELLOW}[1/5] Testing Auth Service...${NC}"
cd auth_service
if [ -d "tests" ]; then
    pytest tests/ -v
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Auth Service tests failed${NC}"
        failed=1
    else
        echo -e "${GREEN}✅ Auth Service tests passed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No tests directory found${NC}"
fi
cd ..

# Inventario Service
echo ""
echo -e "${YELLOW}[2/5] Testing Inventario Service...${NC}"
cd inventario_service
if [ -d "tests" ]; then
    pytest tests/ -v
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Inventario Service tests failed${NC}"
        failed=1
    else
        echo -e "${GREEN}✅ Inventario Service tests passed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No tests directory found${NC}"
fi
cd ..

# Historia Clinica Service
echo ""
echo -e "${YELLOW}[3/5] Testing Historia Clinica Service...${NC}"
cd historia_clinica_service
if [ -d "tests" ]; then
    pytest tests/ -v
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Historia Clinica Service tests failed${NC}"
        failed=1
    else
        echo -e "${GREEN}✅ Historia Clinica Service tests passed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No tests directory found${NC}"
fi
cd ..

# Facturacion Service
echo ""
echo -e "${YELLOW}[4/5] Testing Facturacion Service...${NC}"
cd facturacion_service
if [ -d "tests" ]; then
    pytest tests/ -v
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Facturacion Service tests failed${NC}"
        failed=1
    else
        echo -e "${GREEN}✅ Facturacion Service tests passed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No tests directory found${NC}"
fi
cd ..

# Citas Service
echo ""
echo -e "${YELLOW}[5/5] Testing Citas Service...${NC}"
cd citas_service
if [ -d "tests" ]; then
    pytest tests/ -v
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Citas Service tests failed${NC}"
        failed=1
    else
        echo -e "${GREEN}✅ Citas Service tests passed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No tests directory found${NC}"
fi
cd ..

echo ""
echo "=================================="
if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✅ Todos los tests pasaron exitosamente!${NC}"
else
    echo -e "${RED}❌ Algunos tests fallaron${NC}"
    exit 1
fi
echo "=================================="
