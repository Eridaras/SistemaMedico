# 👋 Guía de Onboarding - Sistema Médico

Bienvenido al equipo de desarrollo del Sistema Médico. Este documento define los estándares y flujos de trabajo para mantener la calidad y seguridad de nuestro monorepo privado.

## 🛠️ Herramientas Recomendadas

### VS Code
Recomendamos usar Visual Studio Code con las siguientes extensiones:
*   **Python** (Microsoft)
*   **ESLint** (Microsoft)
*   **Prettier** (Prettier)
*   **Tailwind CSS IntelliSense**
*   **Docker** (Microsoft)

## 🔄 Flujo de Trabajo (Git Flow)

Este es un proyecto privado, pero mantenemos un rigor profesional en el control de versiones.

1.  **Ramas (Branches)**:
    *   `main`: Producción. Código estable.
    *   `develop`: (Opcional) Integración.
    *   `feature/nombre-feature`: Para nuevas funcionalidades. Ejemplo: `feature/login-pacientes`.
    *   `fix/bug-descripcion`: Para corrección de errores. Ejemplo: `fix/error-calculo-iva`.

2.  **Commits**:
    *   Usar español.
    *   Seguir el formato convencional: `Tipo: Descripción`.
    *   Tipos comunes:
        *   `Feat`: Nueva funcionalidad.
        *   `Fix`: Corrección de error.
        *   `Docs`: Cambios en documentación.
        *   `Style`: Formato, puntos y comas (no lógica).
        *   `Refactor`: Cambio de código sin cambiar lógica.

    *Ejemplo:* `Feat: Agregar validación de cédula en formulario de paciente`

3.  **Pull Requests (PR)**:
    *   Nunca hacer push directo a `main` a menos que seas el líder del proyecto.
    *   Revisar tu propio código antes de solicitar review.

## 🔐 Seguridad y Credenciales

*   **Variables de Entorno**: Solicita el archivo `.env` actualizado al administrador del proyecto.
*   **Base de Datos**: Usamos Neon.tech. No compartir la URL de conexión en canales públicos (Discord, WhatsApp).
*   **Acceso**: Si necesitas invitar a un colaborador, solicita permiso primero.

## 🧪 Calidad de Código

*   **Frontend**: No dejar `console.log` en código de producción. Usar tipos de TypeScript siempre que sea posible.
*   **Backend**: Documentar nuevos endpoints en Swagger. Mantener los modelos Pydantic actualizados.

---
**¡Feliz codificación!** Si tienes dudas, pregunta en el canal de desarrollo.
