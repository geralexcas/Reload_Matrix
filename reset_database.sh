#!/bin/bash

set -e

echo "============================================="
echo "🔄 REINICIANDO BASE DE DATOS"
echo "============================================="

# Cambiar al directorio del proyecto
cd /home/geralexcas/Reload_Matrix_II

# 1. Detener todos los contenedores
echo ""
echo "📦 Deteniendo contenedores..."
docker compose down

# 2. Eliminar volumen de datos (BORRA TODO)
echo ""
echo "🗑️  Eliminando volumen de datos..."
docker volume rm reload_matrix_ii_postgres_data 2>/dev/null || true
docker volume rm reload_matrix_ii_postgres_data 2>/dev/null || echo "  (volumen ya eliminado)"

# 3. Verificar que el volumen se eliminó
echo ""
echo "✅ Volumen eliminado"

# 4. Iniciar solo la base de datos
echo ""
echo "📀 Iniciando base de datos..."
docker compose up -d db

# 5. Esperar a que la base de datos esté lista
echo ""
echo "⏳ Esperando que la base de datos esté lista..."
for i in {1..30}; do
    if docker compose exec -T db pg_isready -U user -d business_db >/dev/null 2>&1; then
        echo "✅ Base de datos lista!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Error: La base de datos no respondió a tiempo"
        exit 1
    fi
    sleep 1
done

# 6. Iniciar backend (ejecuta migraciones automáticamente)
echo ""
echo "🚀 Iniciando backend (ejecuta migraciones automáticamente)..."
docker compose up -d backend

# 7. Esperar a que backend esté listo
echo ""
echo "⏳ Esperando que el backend esté listo..."
for i in {1..20}; do
    if curl -s http://localhost:8001/ >/dev/null 2>&1; then
        echo "✅ Backend listo!"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "⚠️  Backend tardó más de lo normal, continuando..."
    fi
    sleep 2
done

# 8. Iniciar frontend
echo ""
echo "🌐 Iniciando frontend..."
docker compose up -d frontend

# 9. Verificar estado final
echo ""
echo "============================================="
echo "✅ RESET COMPLETADO!"
echo "============================================="
echo ""
echo "📋 DATOS DE ACCESO:"
echo "   📧 Email: admin@admin.com"
echo "   🔑 Password: admin123"
echo ""
echo "🌐 URLs:"
echo "   - Frontend: http://localhost:8081"
echo "   - Backend:  http://localhost:8001"
echo ""
echo "📊 Estado de contenedores:"
docker compose ps

echo ""
echo "ℹ️  La empresa demo y el plan de cuentas se crean automáticamente"
echo "    al iniciar sesión por primera vez."