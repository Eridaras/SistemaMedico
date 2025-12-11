# 🚀 Inicio Rápido - Backend Microservicios

## Pasos para iniciar el sistema

### 1. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
# La URL de la base de datos ya está configurada por defecto
```

### 2. Instalar dependencias

**Windows:**
```bash
install.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

### 3. Ejecutar todos los servicios

**Windows:**
```bash
run_all.bat
```

**Linux/Mac:**
```bash
chmod +x run_all.sh
./run_all.sh
```

### 4. Verificar que todo funciona

Abrir en el navegador o usar curl:

```bash
# Auth Service
curl http://localhost:5001/api/auth/health

# Inventario
curl http://localhost:5002/api/inventario/health

# Historia Clínica
curl http://localhost:5003/api/historia-clinica/health

# Facturación
curl http://localhost:5004/api/facturacion/health

# Citas
curl http://localhost:5005/api/citas/health
```

Si todos responden `{"success": true, "data": {"status": "healthy", "service": "..."}}`, ¡todo está funcionando! ✅

## 🎯 Próximos Pasos

### 1. Crear un usuario inicial

```bash
POST http://localhost:5001/api/auth/register
Content-Type: application/json

{
  "email": "admin@clinica.com",
  "password": "admin123",
  "full_name": "Administrador",
  "role_id": 1
}
```

### 2. Hacer login

```bash
POST http://localhost:5001/api/auth/login
Content-Type: application/json

{
  "email": "admin@clinica.com",
  "password": "admin123"
}
```

Guardar el `token` que se retorna.

### 3. Usar el token en las siguientes peticiones

```bash
GET http://localhost:5001/api/auth/me
Authorization: Bearer <tu-token>
```

## 📚 Documentación Completa

Ver [README.md](README.md) para:
- Lista completa de endpoints
- Arquitectura detallada
- Troubleshooting
- Configuración avanzada

## 🛠️ Servicios y Puertos

| Servicio | Puerto | URL Base |
|----------|--------|----------|
| Autenticación | 5001 | http://localhost:5001/api/auth |
| Inventario | 5002 | http://localhost:5002/api/inventario |
| Historia Clínica | 5003 | http://localhost:5003/api/historia-clinica |
| Facturación | 5004 | http://localhost:5004/api/facturacion |
| Citas | 5005 | http://localhost:5005/api/citas |

## ❓ Problemas Comunes

### Error de base de datos
- Verificar que `DATABASE_URL` en `.env` es correcta
- Verificar que las tablas están creadas (ver `arquitecturaBD.md`)

### Puerto en uso
- Cambiar los puertos en `.env`
- O cerrar el proceso que esté usando el puerto

### Módulo no encontrado
```bash
pip install -r <servicio>/requirements.txt
```

---

**¡Listo para desarrollar! 🎉**
