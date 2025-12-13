# 🏥 Sistema Médico - Clínica Bienestar

> **Sistema Integral de Gestión Hospitalaria con Facturación Electrónica SRI**

[![Status](https://img.shields.io/badge/Estado-Desarrollo_Activo-blue)](https://github.com/tu-usuario/sistema-medico)
[![Version](https://img.shields.io/badge/Versión-1.1.0-green)](CHANGELOG.md)

---

## 🤖 ¿Eres un Agente de IA o Nuevo Desarrollador?

**STOP! LEE ESTO PRIMERO:**
Hemos preparado un documento de contexto maestro que explica TODA la arquitectura, estado actual y reglas del proyecto. Es vital que lo leas antes de realizar cambios.

👉 **[LEER CONTEXTO MAESTRO DEL PROYECTO (docs/CONTEXTO_AGENTE.md)](docs/CONTEXTO_AGENTE.md)** 👈

---

## 🚀 Inicio Rápido

### Requisitos
- Node.js 18+
- Python 3.9+
- PostgreSQL
- Git

### Instalación

1. **Clonar repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/sistema-medico.git
   cd sistema-medico
   ```

2. **Backend (Microservicios):**
   ```bash
   cd backend
   # Crear entorno virtual (opcional pero recomendado)
   python -m venv venv
   .\venv\Scripts\activate
   
   # O usar script automático
   .\install.bat
   
   # Iniciar servicios
   .\run_all.bat
   ```

3. **Frontend (Next.js):**
   ```bash
   cd Frontend
   npm install
   npm run dev
   ```

4. **Acceso:**
   - Web: `http://localhost:9002`
   - Admin: `admin@clinica.com` / `admin123`

## 📚 Documentación

- **[Contexto Técnico (Agentes)](docs/CONTEXTO_AGENTE.md)** - Arquitectura y reglas.
- **[Plan de Implementación](docs/PLAN_IMPLEMENTACION.md)** - Roadmap SRI y Datos.
- **[Estrategia de Pruebas](docs/ESTRATEGIA_PRUEBAS.md)** - QA.
- **[Changelog](CHANGELOG.md)** - Historial de cambios.

## 🏗️ Arquitectura

El sistema utiliza una arquitectura de microservicios:
- **Frontend:** Next.js 15 + Tailwind + Shadcn/UI
- **Backend:** Python Flask (5 servicios independientes)
- **Base de Datos:** PostgreSQL
- **Facturación:** XML/SOAP Nativo SRI Ecuador

## 📄 Licencia

Este proyecto es software propietario de Clínica Bienestar.
