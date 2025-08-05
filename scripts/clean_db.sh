#!/bin/bash

# Script para limpiar la base de datos
# Uso: ./scripts/clean_db.sh [--auto]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con colores
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si estamos en el directorio correcto
if [ ! -f "app/main.py" ]; then
    print_error "Este script debe ejecutarse desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    print_warning "No se encontró el entorno virtual. Creando uno nuevo..."
    python3 -m venv venv
fi

# Activar el entorno virtual
print_info "Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias si es necesario
if [ ! -f "venv/lib/python*/site-packages/fastapi" ]; then
    print_info "Instalando dependencias..."
    pip install -r requirements.txt
fi

# Verificar argumentos
if [ "$1" = "--auto" ]; then
    print_info "Ejecutando limpieza automática de la base de datos..."
    python scripts/clean_database_auto.py
else
    print_info "Ejecutando limpieza interactiva de la base de datos..."
    python scripts/clean_database.py
fi

# Verificar el resultado
if [ $? -eq 0 ]; then
    print_success "Limpieza de la base de datos completada exitosamente"
else
    print_error "Error durante la limpieza de la base de datos"
    exit 1
fi 