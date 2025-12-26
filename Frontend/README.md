# 🏥 Sistema Médico - Frontend

Frontend moderno del Sistema de Gestión Clínica, desarrollado con Next.js 15, React 19 y Tailwind CSS.

## 📋 Índice

- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Desarrollo](#-desarrollo)
- [Arquitectura](#-arquitectura)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Tecnologías](#-tecnologías)
- [Integración Backend](#-integración-backend)
- [Componentes Principales](#-componentes-principales)
- [Testing](#-testing)
- [Deployment](#-deployment)

---

## 🔧 Requisitos

- **Node.js**: 22.12.0 LTS (especificada en `.nvmrc`)
- **npm**: 10.x o superior (incluida con Node.js 22)
- **Backend**: Microservicios corriendo (puertos 5001-5006)

### Instalación de Node.js

#### Con `nvm` (recomendado)
```bash
nvm install
nvm use
```

#### Con `fnm`
```bash
fnm install
fnm use
```

---

## 🚀 Instalación

```bash
# Instalar dependencias
npm install

# Copiar variables de entorno
cp .env.example .env.local

# Editar variables de entorno
nano .env.local
```

### Variables de Entorno

```env
# API Backend
NEXT_PUBLIC_API_URL=http://localhost:5001

# Firebase (opcional)
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-auth-domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id

# Genkit AI (opcional)
GOOGLE_GENAI_API_KEY=your-genai-api-key
```

---

## 💻 Desarrollo

### Iniciar Servidor de Desarrollo

```bash
npm run dev
```

El servidor estará disponible en `http://localhost:9002`.

### Características de Desarrollo

- **Hot Reload**: Recarga automática con Turbopack
- **Fast Refresh**: Actualización rápida de componentes React
- **TypeScript**: Verificación de tipos en tiempo real
- **Tailwind JIT**: Compilación Just-In-Time de CSS

### Scripts Disponibles

| Comando | Descripción |
|---------|-------------|
| `npm run dev` | Inicia el servidor de desarrollo con Turbopack |
| `npm run build` | Genera el build de producción |
| `npm start` | Inicia el servidor en modo producción |
| `npm run lint` | Ejecuta ESLint para verificar código |
| `npm run typecheck` | Verifica tipos de TypeScript |
| `npm run genkit:dev` | Inicia el servidor Genkit para desarrollo de AI |
| `npm run genkit:watch` | Inicia Genkit con hot reload |

---

## 🏗️ Arquitectura

### App Router (Next.js 15)

El proyecto utiliza el **App Router** de Next.js con la siguiente estructura:

```
src/app/
├── (auth)/              # Rutas públicas (login, registro)
│   └── login/
│       └── page.tsx
├── (app)/               # Rutas protegidas (dashboard)
│   ├── dashboard/
│   ├── patients/
│   ├── appointments/
│   ├── inventory/
│   ├── billing/
│   └── layout.tsx
├── api/                 # API Routes (proxy al backend)
├── layout.tsx           # Layout raíz
└── page.tsx             # Página principal
```

### Server vs Client Components

- **Server Components** (por defecto): Renderizados en el servidor
- **Client Components** (`"use client"`): Interactivos en el navegador

### Middleware

- **Autenticación**: Protege rutas basadas en JWT
- **Redirecciones**: Redirige usuarios no autenticados

---

## 📁 Estructura del Proyecto

```
Frontend/
├── src/
│   ├── app/                    # App Router (Next.js 15)
│   │   ├── (auth)/             # Grupo de rutas públicas
│   │   │   └── login/
│   │   ├── (app)/              # Grupo de rutas protegidas
│   │   │   ├── dashboard/
│   │   │   ├── patients/
│   │   │   ├── appointments/
│   │   │   ├── inventory/
│   │   │   ├── billing/
│   │   │   └── layout.tsx      # Layout con sidebar
│   │   ├── api/                # API Routes (proxy)
│   │   ├── layout.tsx          # Root layout
│   │   └── globals.css         # Estilos globales
│   ├── components/             # Componentes reutilizables
│   │   ├── ui/                 # Shadcn/UI components
│   │   ├── dashboard/          # Componentes del dashboard
│   │   ├── sidebar.tsx         # Navegación lateral
│   │   └── page-transition.tsx # Animaciones de página
│   ├── actions/                # Server Actions
│   │   └── auth.ts             # Acciones de autenticación
│   ├── lib/                    # Utilidades
│   │   ├── utils.ts            # Funciones helper
│   │   └── api.ts              # Cliente API
│   ├── hooks/                  # Custom Hooks
│   │   ├── use-auth.ts         # Hook de autenticación
│   │   └── use-toast.ts        # Hook de notificaciones
│   └── ai/                     # Genkit AI
│       └── genkit.ts           # Configuración AI
├── public/                     # Archivos estáticos
│   ├── images/
│   └── icons/
├── docs/                       # Documentación
│   └── blueprint.md            # Guía de diseño UI/UX
├── .env.example                # Variables de entorno de ejemplo
├── .nvmrc                      # Versión de Node.js
├── next.config.ts              # Configuración Next.js
├── tailwind.config.ts          # Configuración Tailwind
├── tsconfig.json               # Configuración TypeScript
└── package.json                # Dependencias

```

### Descripción de Carpetas

#### `src/app/`
- **App Router** de Next.js 15
- Organización por grupos de rutas: `(auth)` y `(app)`
- Layouts anidados para estructura modular

#### `src/components/`
- Componentes UI de Shadcn/UI (`ui/`)
- Componentes específicos de módulos (`dashboard/`, `patients/`)
- Componentes compartidos (`sidebar.tsx`, `page-transition.tsx`)

#### `src/actions/`
- **Server Actions** de Next.js
- Lógica de negocio que se ejecuta en el servidor
- Ejemplo: autenticación, mutaciones de datos

#### `src/lib/`
- Utilidades y funciones helper
- Cliente HTTP para consumir backend
- Configuraciones compartidas

#### `src/hooks/`
- Custom React Hooks
- Lógica reutilizable del cliente
- Estado global compartido

---

## 🛠️ Tecnologías

### Core

| Tecnología | Versión | Descripción |
|------------|---------|-------------|
| [Next.js](https://nextjs.org/) | 15.5.9 | Framework React con SSR/SSG |
| [React](https://react.dev/) | 19.2.1 | Librería UI |
| [TypeScript](https://www.typescriptlang.org/) | 5.6.3 | Tipado estático |

### UI/UX

| Tecnología | Descripción |
|------------|-------------|
| [Tailwind CSS](https://tailwindcss.com/) | Framework CSS utility-first |
| [Shadcn/UI](https://ui.shadcn.com/) | Componentes accesibles |
| [Radix UI](https://www.radix-ui.com/) | Primitivos UI sin estilos |
| [Framer Motion](https://www.framer.com/motion/) | Animaciones y transiciones |
| [Lucide Icons](https://lucide.dev/) | Iconos SVG |

### Datos y Estado

| Tecnología | Descripción |
|------------|-------------|
| [SWR](https://swr.vercel.app/) | Data fetching y caché |
| [Zustand](https://zustand-demo.pmnd.rs/) | Estado global ligero |

### AI/ML

| Tecnología | Descripción |
|------------|-------------|
| [Firebase Genkit](https://firebase.google.com/docs/genkit) | Integración AI/ML |
| [Google Gemini](https://ai.google.dev/) | Modelo de lenguaje |

---

## 🔌 Integración Backend

### Estado de Conexión

El frontend está **100% conectado** a los microservicios del backend:

| Módulo | Servicio Backend | Estado | Endpoints |
|--------|------------------|--------|-----------|
| **🔐 Autenticación** | `auth_service:5001` | 🟢 Conectado | `/api/auth/*` |
| **👥 Pacientes** | `historia_clinica_service:5003` | 🟢 Conectado | `/api/historia-clinica/*` |
| **📦 Inventario** | `inventario_service:5002` | 🟢 Conectado | `/api/inventario/*` |
| **📅 Citas** | `citas_service:5005` | 🟢 Conectado | `/api/citas/*` |
| **💰 Facturación** | `facturacion_service:5004` | 🟢 Conectado | `/api/facturacion/*` |
| **📊 Dashboard** | Múltiples servicios | 🟢 Conectado | Agregado |

### Proxy de API

El frontend usa **Next.js rewrites** para hacer proxy a los microservicios:

```typescript
// next.config.ts
rewrites: async () => [
  { source: '/api/auth/:path*', destination: 'http://localhost:5001/api/auth/:path*' },
  { source: '/api/inventario/:path*', destination: 'http://localhost:5002/api/inventario/:path*' },
  { source: '/api/historia-clinica/:path*', destination: 'http://localhost:5003/api/historia-clinica/:path*' },
  { source: '/api/facturacion/:path*', destination: 'http://localhost:5004/api/facturacion/:path*' },
  { source: '/api/citas/:path*', destination: 'http://localhost:5005/api/citas/:path*' },
]
```

### Cliente HTTP

```typescript
// src/lib/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para agregar JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
```

---

## 🧩 Componentes Principales

### Dashboard
- **KPIs Animados**: Ingresos, pacientes, citas del día
- **Gráficos**: Chart.js con datos reales
- **Lista de Citas**: Citas del día con acciones rápidas

### Pacientes
- **Tabla Interactiva**: Búsqueda, filtrado, paginación
- **Formulario de Creación**: Validación con React Hook Form
- **Vista Detalle**: Historia clínica completa

### Citas
- **Calendario Mensual**: Navegación por mes
- **Panel de Detalles**: Información completa de la cita
- **Estados**: PENDING, CONFIRMED, COMPLETED, CANCELLED

### Inventario
- **Gestión de Productos**: CRUD completo
- **Control de Stock**: Alertas de stock bajo
- **Filtros**: Por categoría y estado

### Facturación
- **Generador de Facturas**: Creación paso a paso
- **Lista de Facturas**: Historial completo
- **Dashboard Financiero**: Ingresos vs Egresos

---

## 🧪 Testing

```bash
# Ejecutar tests (cuando estén configurados)
npm run test

# Tests con cobertura
npm run test:coverage

# Tests en modo watch
npm run test:watch
```

---

## 🚢 Deployment

### Build de Producción

```bash
npm run build
npm start
```

### Firebase App Hosting

```bash
firebase deploy --only hosting
```

### Vercel

```bash
vercel --prod
```

### Docker

```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

---

## 📚 Recursos Adicionales

- **Blueprint UI/UX**: [docs/blueprint.md](docs/blueprint.md)
- **Documentación Backend**: [../backend/README.md](../backend/README.md)
- **Guía de Deployment**: [../docs/DEPLOYMENT_GUIDE.md](../docs/DEPLOYMENT_GUIDE.md)

---

**Última actualización:** 2025-12-17
