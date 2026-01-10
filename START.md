# 🚀 INICIO RÁPIDO - Sistema Médico

## ⚡ Comandos Rápidos

### Primera Vez (Build Completo)
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Desarrollo Diario
```bash
docker-compose up
# O en modo detached:
docker-compose up -d
```

### Ver Logs en Tiempo Real
```bash
docker-compose logs -f
# Solo un servicio específico:
docker-compose logs -f auth-service
docker-compose logs -f frontend
```

### Rebuild Solo un Servicio
```bash
docker-compose build --no-cache auth-service
docker-compose up -d auth-service
```

### Detener Todo
```bash
docker-compose down
# Con limpieza de volúmenes:
docker-compose down -v
```

## 🌐 Accesos del Sistema

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Aplicación Principal** | http://localhost | Entrada única (Traefik) |
| **Traefik Dashboard** | http://localhost/traefik | Ver rutas y servicios |
| **Auth Service Swagger** | http://localhost/api/auth/docs | Documentación API Auth |
| **Inventario Swagger** | http://localhost/api/inventario/docs | Documentación API Inventario |
| **Historia Clínica Swagger** | http://localhost/api/historia-clinica/docs | Documentación API Historia |
| **Facturación Swagger** | http://localhost/api/facturacion/docs | Documentación API Facturación |
| **Citas Swagger** | http://localhost/api/citas/docs | Documentación API Citas |
| **Logs Swagger** | http://localhost/api/logs/docs | Documentación API Logs |
| **Notifications Swagger** | http://localhost/api/notifications/docs | Documentación API Notificaciones |

## 🔑 Credenciales de Prueba

```
Email: admin@clinica.com
Password: admin123
```

## 📁 Arquitectura del Sistema

```
Cliente → http://localhost:80 (Traefik)
         ↓
   [traefik-dynamic.yml] ← Configuración de rutas (File Provider)
         ↓
    ┌────────────────────────────────────────────────────┐
    │  Routers (definidos en traefik-dynamic.yml):      │
    │  /                    → Frontend :3000 (interno)   │
    │  /api/auth            → Auth Service :5000         │
    │  /api/inventario      → Inventario Service :5000   │
    │  /api/historia-clinica → Historia Service :5000    │
    │  /api/facturacion     → Facturacion Service :5000  │
    │  /api/citas           → Citas Service :5000        │
    │  /api/logs            → Logs Service :5000         │
    │  /api/notifications   → Notifications Service :5000│
    │  /traefik             → Traefik Dashboard          │
    └────────────────────────────────────────────────────┘

IMPORTANTE:
- Todos los puertos internos (3000, 5000) NO son accesibles desde el host
- Solo el puerto 80 de Traefik está expuesto
- Todo el enrutamiento es INTERNO vía redes Docker
- Las rutas se configuran en traefik-dynamic.yml (NO auto-discovery)
```

## 🛠️ Desarrollo

### Hot-Reload Automático
- ✅ **Frontend**: Los cambios en `Frontend/` se reflejan automáticamente
- ✅ **Backend**: Los cambios en `backend/*/` se reflejan automáticamente (gunicorn --reload)
- ✅ **Common**: Los cambios en `backend/common/` requieren restart manual del servicio

### Restart Manual de un Servicio
```bash
docker-compose restart auth-service
docker-compose restart frontend
```

### Agregar o Modificar Rutas de Traefik
```bash
# 1. Editar traefik-dynamic.yml
# 2. Reiniciar Traefik para aplicar cambios
docker-compose restart traefik
# Nota: El auto-reload (watch) puede no funcionar en Windows
```

### Acceder a un Contenedor
```bash
docker exec -it medical_auth bash
docker exec -it medical_frontend sh
```

### Ver Estado de Servicios
```bash
docker-compose ps
```

## ⚠️ Troubleshooting

### Error: "port is already allocated"
```bash
# Ver qué está usando el puerto 80
netstat -ano | findstr :80
# Matar el proceso o cambiar puerto en docker-compose.yml
```

### Error: "no configuration has been provided"
```bash
# Verificar que los labels de Traefik sean correctos
docker-compose config
```

### Frontend muestra 502 Bad Gateway
```bash
# Ver logs del frontend
docker-compose logs frontend
# Verificar que Next.js está corriendo internamente
docker-compose ps frontend
```

### Backend muestra 401 Unauthorized
```bash
# Verificar que el token esté en localStorage
# Abrir DevTools → Application → Local Storage
# Debe haber key "token" con valor JWT
```

### No se reflejan los cambios
```bash
# Rebuild sin caché
docker-compose build --no-cache {service-name}
docker-compose up -d {service-name}
```

### Limpiar TODO y empezar de cero
```bash
docker-compose down -v
docker system prune -a --volumes
docker-compose build --no-cache
docker-compose up
```

## 📊 Verificar que Todo Funciona

1. **Traefik Dashboard**: http://localhost/traefik
   - Debes ver 8 routers (frontend + 7 services)

2. **Health Checks** (via Traefik):
   ```bash
   curl http://localhost/api/auth/health
   curl http://localhost/api/inventario/health
   curl http://localhost/api/historia-clinica/health
   curl http://localhost/api/facturacion/health
   curl http://localhost/api/citas/health
   curl http://localhost/api/logs/health
   curl http://localhost/api/notifications/health
   ```

3. **Login via Traefik**:
   ```bash
   curl -X POST http://localhost/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@clinica.com","password":"admin123"}'
   ```

## 🎯 Workflow Típico de Desarrollo

1. **Iniciar sistema**: `docker-compose up`
2. **Abrir navegador**: http://localhost
3. **Login**: admin@clinica.com / admin123
4. **Hacer cambios** en código (Frontend/ o backend/)
5. **Ver cambios automáticamente** (hot-reload)
6. **Detener**: `Ctrl+C` o `docker-compose down`

## 📝 Notas Importantes

### Arquitectura de Routing
- **Traefik File Provider**: El sistema usa File Provider en lugar de Docker Provider
- **Configuración Estática**: Las rutas se definen en `traefik-dynamic.yml`
- **Sin Auto-Discovery**: Al agregar un nuevo servicio, debes editar manualmente `traefik-dynamic.yml`
- **Ventaja**: Funciona de forma confiable en Windows/WSL2 sin problemas de socket

### Seguridad y Puertos
- **UN SOLO PUERTO EXPUESTO**: Solo el puerto 80 de Traefik es visible al host
- **Comunicación Interna**: Todos los servicios se comunican internamente vía redes Docker
- **NO** intentes acceder directamente a puertos como 3000, 5000 - no están expuestos
- **NUNCA** expongas el puerto 80 en producción sin HTTPS (usa certificados SSL/TLS)
- **SIEMPRE** usa variables de entorno para secrets en producción

### Base de Datos y Cache
- **JWT_SECRET_KEY** debe ser aleatorio en producción
- **DATABASE_URL** apunta a Neon (PostgreSQL cloud) - es compartido
- **Redis** es local y se resetea al hacer `docker-compose down -v`

## 🔒 Seguridad

- [ ] Cambiar `JWT_SECRET_KEY` en producción
- [ ] Usar HTTPS con certificado SSL/TLS
- [ ] Configurar rate limiting en Traefik
- [ ] Habilitar autenticación en Traefik Dashboard
- [ ] Usar secrets de Docker Swarm en producción
