# 📋 Contexto del Proyecto

**Fecha de Auditoría:** 16 de Diciembre, 2025
**Generado por:** AI Factory Audit Ecosystem
**Versión:** 2.0

---

## 🎯 Visión General

**Sistema Médico Integral** es una plataforma SaaS de gestión clínica completa diseñada para facilitar la operación de consultorios médicos en Ecuador. El sistema integra la gestión de pacientes, agenda de citas, historia clínica electrónica, facturación electrónica (SRI), inventario de productos médicos y control financiero en una solución cohesiva.

### Objetivo del Proyecto

Proporcionar una herramienta moderna, escalable y conforme a normativas ecuatorianas que permita a profesionales médicos:
- Gestionar historias clínicas electrónicas de forma segura
- Coordinar citas y disponibilidad de agenda
- Emitir facturas electrónicas válidas ante el SRI
- Controlar inventario y vincular tratamientos con productos
- Analizar métricas financieras y operativas

---

## 🏗️ Arquitectura del Sistema

### Patrón Arquitectónico

**Monorepo con Backend de Microservicios + Frontend Monolítico**

```
Test2/
├── Backend/              # Python/Flask Microservices
│   ├── auth_service/      (Puerto 5001)
│   ├── inventario_service/(Puerto 5002)
│   ├── historia_clinica_service/ (Puerto 5003)
│   ├── facturacion_service/ (Puerto 5004)
│   ├── citas_service/     (Puerto 5005)
│   ├── logs_service/      (Puerto 5006)
│   └── common/            # Utilidades compartidas
│
└── Frontend/             # Next.js 15 + React 19
    └── src/              # Aplicación web única
```

### Comunicación entre Servicios

- **Backend-Backend**: HTTP REST (módulo `service_client.py`)
- **Frontend-Backend**: HTTP REST con autenticación JWT
- **Base de Datos**: PostgreSQL centralizado (Neon.tech Serverless)

---

## 🔑 Componentes Principales

### Backend (Microservicios)

| Servicio | Puerto | Responsabilidad | Estado |
|----------|--------|----------------|--------|
| **Auth Service** | 5001 | Login, Registro, JWT, RBAC | ✅ Funcional |
| **Inventario Service** | 5002 | Productos, Tratamientos, Motor de Recetas | ✅ Funcional |
| **Historia Clínica Service** | 5003 | Pacientes, Antecedentes, Notas Médicas | ✅ Funcional |
| **Facturación Service** | 5004 | Facturas SRI (XML/RIDE), Gastos, Dashboard | ✅ Funcional |
| **Citas Service** | 5005 | Agendamiento, Disponibilidad | ✅ Funcional |
| **Logs Service** | 5006 | Auditoría de acciones del sistema | ✅ Funcional |

### Frontend (Web Application)

| Módulo | Tecnología | Estado | Completitud |
|--------|-----------|--------|-------------|
| **Autenticación** | Next.js Auth | 🟡 Básico | 40% |
| **Dashboard** | Recharts | 🟡 Maqueta | 30% |
| **Pacientes** | React Hook Form + Zod | 🟡 Parcial | 50% |
| **Citas** | React Day Picker | 🟡 Básico | 40% |
| **Facturación** | Custom Components | 🔴 Incompleto | 20% |
| **Inventario** | - | 🔴 No implementado | 0% |
| **Configuración** | - | 🔴 No implementado | 0% |

---

## 👥 Roles y Permisos

El sistema implementa RBAC (Role-Based Access Control) con los siguientes roles:

| Rol | Descripción | Permisos Clave |
|-----|-------------|----------------|
| **Administrador** | Control total del sistema | Todos los módulos + Gestión de usuarios |
| **Médico** | Profesional de salud | Historia Clínica, Citas, Recetas |
| **Recepcionista** | Personal de apoyo | Agenda, Pacientes (lectura), Facturación |
| **Contador** | Gestión financiera | Facturación, Gastos, Reportes |

---

## 🔐 Seguridad y Normativas

### Normativa Ecuatoriana

- **Validación de Cédula**: Algoritmo Módulo 10
- **Validación de RUC**: Verificación de dígitos según tipo de contribuyente
- **Facturación Electrónica**: Generación de XML conforme a especificaciones SRI
- **Firma Digital**: Integración con certificados .p12 para autenticar documentos

### Seguridad Implementada

- **Autenticación**: JWT (JSON Web Tokens) con expiración configurable
- **Hashing de Contraseñas**: bcrypt con factor de costo adecuado
- **CORS**: Configuración de orígenes permitidos por variable de entorno
- **Base de Datos**: Conexión mediante pooling seguro con psycopg2
- **Logging**: Registro de acciones críticas en `logs_service`

---

## 📊 Estado de Desarrollo Actual

### Fase 1: Backend Cleanup (✅ COMPLETADO)
- Corrección de estructura de carpetas duplicada
- Consolidación de microservicios
- Documentación de arquitectura

### Fase 2: Integración Frontend-Backend (🔴 EN PROGRESO - 35%)
- Cliente HTTP con interceptores JWT: ⏳ Pendiente
- Integración Auth Service: ⏳ Pendiente
- Módulo de Pacientes conectado: ⏳ Pendiente

### Fase 3: Módulos Core (⏸️ PAUSADO)
- Inventario UI
- Dashboard con datos reales
- Calendario de citas avanzado

### Fase 4: Facturación SRI (⏸️ PAUSADO)
- UI de emisión de facturas
- Visualización de RIDE (PDF)
- Integración con SRI Producción

---

## 🎯 Objetivos de Negocio

### Corto Plazo (0-3 meses)
- Completar integración Frontend-Backend
- Implementar módulos críticos (Inventario, Facturación)
- Conectar todos los endpoints con la UI

### Mediano Plazo (3-6 meses)
- Despliegue en ambiente de producción
- Onboarding de primeros clientes
- Optimización de rendimiento

### Largo Plazo (6-12 meses)
- Escalamiento multi-tenant
- Módulo de reportes avanzados
- Integración con WhatsApp/Email para notificaciones

---

## 📈 Métricas del Proyecto

### Código
- **Backend**: ~6 microservicios, ~15,000 líneas de Python
- **Frontend**: ~50 componentes React, ~8,000 líneas de TypeScript
- **Documentación**: 5 archivos principales en `/docs`

### Cobertura de Tests
- **Backend**: ~40% (pytest)
- **Frontend**: 0% (no implementado)

### Deuda Técnica Identificada
- Versión de Node.js cerca de EOL (18 → 22 recomendado)
- PostgreSQL sin versión fijada ("latest")
- pytest desactualizado (7.4.3 → 8.3 recomendado)
- Falta de tests en Frontend
- Configuraciones de CORS demasiado permisivas en algunos servicios

---

## 🔗 Dependencias Externas

### Infraestructura
- **Base de Datos**: Neon.tech (PostgreSQL Serverless)
- **Hosting**: Por definir (AWS/GCP/Azure)
- **CDN**: Por definir

### Servicios Externos
- **SRI**: Servicio de Rentas Internas (Facturación Electrónica)
- **Firebase**: Autenticación y Genkit AI (Frontend)
- **Google Genai**: Integración de IA generativa

---

## 📚 Recursos y Referencias

### Documentación del Proyecto
- [README Principal](../README.md)
- [Guía de Onboarding](ONBOARDING.md)
- [Análisis Integral del Estado](ANALISIS_INTEGRAL_ESTADO.md)
- [Arquitectura de Base de Datos](../Backend/docs/arquitecturaBD.md)

### Repositorios Relacionados
- Repositorio privado en Git (detalle confidencial)

---

**Última Actualización:** 2025-12-16
**Responsable:** Eridaras Dev Team
