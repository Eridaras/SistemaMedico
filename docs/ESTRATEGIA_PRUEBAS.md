# 🧪 Estrategia y Guía de Pruebas - Sistema Médico

Este documento define cómo validar la funcionalidad del sistema, tanto para agentes de IA como para desarrolladores humanos. **Todo cambio debe ser verificado antes de considerarse completo.**

## 1. Niveles de Pruebas

### A. Backend (Validación de Lógica y Datos)
El backend tiene una suite de pruebas automatizadas usando `pytest`.

**Cómo ejecutar:**
1. Navegar a la carpeta `backend`.
2. Ejecutar el script de pruebas correspondiente a tu OS.

**Comandos:**
```bash
# Windows
cd backend
run_tests.bat

# Linux/Mac
cd backend
./run_tests.sh
```

**Qué verifica esto:**
- Conexión a base de datos.
- Creación de usuarios, pacientes, citas y facturas (CRUD).
- Validaciones de negocio (ej: cédulas ecuatorianas válidas).
- Cálculo correcto de impuestos (IVA 15%).

### B. Frontend (Verificación Visual y de Flujo)
Actualmente, las pruebas del frontend son manuales o exploratorias.

**Flujo Crítico de Verificación (Checklist):**
1. **Login:**
   - Ingresar con credenciales inválidas (debe mostrar error).
   - Ingresar con `admin@clinica.com` / `admin123` (debe redirigir al Dashboard).
2. **Navegación:**
   - Verificar que no se pueda acceder a `/dashboard` sin login (redirección a `/login`).
   - El menú lateral debe resaltar la página activa.
3. **Integración con API:**
   - En el Dashboard, los contadores no deben mostrar "0" estático, deben intentar cargar datos (spinner o data real).
   - Si el backend está apagado, debe manejar el error con gracia (toast o mensaje de error).

### C. Pruebas de Integración (End-to-End Manual)
1. **Flujo de Paciente Nuevo:**
   - Crear paciente desde Frontend -> Verificar que aparece en `GET /api/historia-clinica/patients`.
2. **Flujo de Cita:**
   - Agendar cita en Frontend -> Verificar que descuenta disponibilidad (si aplica) y aparece en `GET /api/citas/appointments`.

## 2. Instrucciones para Agentes (AI)

Si eres un agente encargado de una tarea, sigue este protocolo:

1.  **Antes de codificar:**
    *   Revisa `backend/tests/` para entender la estructura de datos esperada.
    *   Si es frontend, revisa `Modelos Frontend/` para alinear estilos.

2.  **Después de codificar (Backend):**
    *   **OBLIGATORIO:** Ejecuta `backend/run_tests.bat` y asegúrate que el "exit code" sea 0.
    *   Si rompes un test existente, tu cambio es incorrecto o el test debe actualizarse.

3.  **Después de codificar (Frontend):**
    *   No hay tests automáticos aún. Tu validación es verificar que:
        *   `npm run build` no arroje errores.
        *   Los componentes se renderizan sin errores de consola.
        *   La estética coincide con el "Modelo Frontend".

## 3. Depuración

Si las pruebas fallan:
1. Revisa los logs del backend en `http://localhost:5006/api/logs/logs` (o en la consola del servidor).
2. Asegúrate que la base de datos (Neon.tech) está accesible.
3. Verifica que las variables de entorno `.env` sean correctas.
