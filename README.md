# Sistema Médico Integral 🏥

> **⚠️ PROYECTO PRIVADO**: Este repositorio contiene código propietario y confidencial. Su acceso y distribución están restringidos exclusivamente al equipo de desarrollo autorizado.

Este monorepo alberga la solución completa para la gestión clínica, integrando un backend robusto basado en microservicios y un frontend moderno de alto rendimiento.

## 📂 Estructura del Proyecto

El repositorio está organizado en dos componentes principales:

*   **`/Backend`**: Servicios RESTful desarrollados en Python/Flask. Maneja la lógica de negocio, base de datos y autenticación.
*   **`/Frontend`**: Aplicación web moderna construida con Next.js. Provee la interfaz de usuario para médicos, recepcionistas y administradores.

## 🚀 Inicio Rápido

### Requisitos Previos

*   **Node.js** (v18 o superior)
*   **Python** (v3.12 o superior)
*   **Docker** (Opcional, para contenedores)
*   **Git**

### Configuración del Entorno

Para levantar el entorno de desarrollo completo, sigue estas instrucciones por componente:

#### 1. Backend (API)

Consulte el [README del Backend](Backend/README.md) para instrucciones detalladas. Resumen rápido:

```bash
cd Backend
# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt (o por servicio individual)

# Configurar variables de entorno
cp .env.example .env
# (Solicitar credenciales de Neon.tech al líder técnico)

# Ejecutar servicios
./run_all.bat
```

#### 2. Frontend (Web)

```bash
cd Frontend
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

La aplicación web estará disponible en `http://localhost:9002` (puerto configurado en `package.json`).

## 🛠️ Stack Tecnológico

### Frontend
*   **Framework**: Next.js 15 (React 19)
*   **Estilos**: Tailwind CSS + Shadcn/UI
*   **Iconos**: Lucide React
*   **IA/GenAI**: Google Genkit + Firebase
*   **Validación**: Zod + React Hook Form

### Backend
*   **Lenguaje**: Python 3.12+
*   **Framework**: Flask (Microservicios)
*   **Base de Datos**: PostgreSQL (Neon.tech Serverless)
*   **Autenticación**: JWT (JSON Web Tokens)
*   **Documentación**: Swagger/OpenAPI

## 📖 Documentación Adicional

*   [Guía de Onboarding y Normas](docs/ONBOARDING.md): Lectura obligatoria para nuevos miembros.
*   [Arquitectura de Base de Datos](Backend/docs/arquitecturaBD.md): Diagramas y esquemas.

## 🔐 Seguridad y Normativas

1.  **Nunca subir archivos `.env`**: Las credenciales locales son personales.
2.  **Datos Sensibles**: No hardcodear contraseñas ni claves API en el código.
3.  **Ramas**: Trabajar siempre en ramas separadas (`feature/nueva-funcionalidad`) y hacer Pull Request a `main`.

---
© Eridaras Dev Team. Todos los derechos reservados.
