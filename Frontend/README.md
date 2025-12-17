# Sistema Médico - Frontend

Este es el frontend del Sistema de Gestión Clínica, desarrollado con Next.js.

## Requisitos del Sistema

- **Node.js**: 22.12.0 LTS (especificada en `.nvmrc`)
- **npm**: 10.x o superior (incluida con Node.js 22)

### Instalación de Node.js

Si usas `nvm` (recomendado):
```bash
nvm install
nvm use
```

Si usas `fnm`:
```bash
fnm install
fnm use
```

## Instalación

```bash
npm install
```

## Desarrollo

```bash
npm run dev
```

El servidor de desarrollo estará disponible en `http://localhost:9002`.

## Build de Producción

```bash
npm run build
npm start
```

## Scripts Disponibles

- `npm run dev` - Inicia el servidor de desarrollo con Turbopack
- `npm run build` - Genera el build de producción
- `npm start` - Inicia el servidor en modo producción
- `npm run lint` - Ejecuta el linter
- `npm run typecheck` - Verifica tipos de TypeScript
- `npm run genkit:dev` - Inicia el servidor Genkit para desarrollo de AI
- `npm run genkit:watch` - Inicia Genkit con hot reload

## Tecnologías

- [Next.js 15](https://nextjs.org/) - Framework React
- [React 19](https://react.dev/) - Librería UI
- [TypeScript 5.6](https://www.typescriptlang.org/) - Tipado estático
- [Tailwind CSS](https://tailwindcss.com/) - Framework CSS
- [Radix UI](https://www.radix-ui.com/) - Componentes accesibles
- [Firebase](https://firebase.google.com/) - Autenticación y servicios
- [Genkit](https://firebase.google.com/docs/genkit) - AI/ML integración

## Estructura del Proyecto

```
src/
├── app/           # Rutas y páginas de Next.js
├── components/    # Componentes reutilizables
├── actions/       # Server Actions
├── lib/           # Utilidades y configuraciones
├── hooks/         # Custom hooks
└── ai/            # Configuración Genkit AI
```

## Variables de Entorno

Crear un archivo `.env.local` basado en `.env.example`:

```env
NEXT_PUBLIC_API_URL=http://localhost:5001
GOOGLE_GENAI_API_KEY=your-api-key
```
