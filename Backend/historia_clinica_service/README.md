# 👨‍⚕️ Historia Clínica Service - Servicio de Historia Clínica

Microservicio de gestión de pacientes y sus historiales médicos del Sistema Médico. Controla datos demográficos, antecedentes y notas clínicas.

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Endpoints](#-endpoints)
- [Modelos de Datos](#-modelos-de-datos)
- [Normativa Ecuador](#-normativa-ecuador)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Testing](#-testing)

---

## ✨ Funcionalidades

- **Gestión de Pacientes**: CRUD completo con validación de cédula ecuatoriana
- **Historia Médica**: Antecedentes, alergias, cirugías, patologías
- **Notas Clínicas**: Registro de evolución por cita médica
- **Búsqueda Avanzada**: Por nombre, cédula, email, teléfono
- **Validación de Documentos**: Cédula y RUC con algoritmo verificador
- **Datos Demográficos**: Edad, género, grupo sanguíneo
- **Relación con Citas**: Historial completo de atenciones

---

## 🌐 Endpoints

### Base URL
```
http://localhost:5003/api/historia-clinica
```

### Documentación Interactiva
```
http://localhost:5003/docs
```

### Lista de Endpoints

#### Pacientes

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/patients` | Listar todos los pacientes | Sí |
| `GET` | `/patients/:id` | Obtener paciente por ID | Sí |
| `GET` | `/patients/search` | Buscar paciente (query params) | Sí |
| `POST` | `/patients` | Crear nuevo paciente | Sí |
| `PUT` | `/patients/:id` | Actualizar paciente | Sí |
| `DELETE` | `/patients/:id` | Eliminar paciente | Sí (Admin) |
| `GET` | `/patients/:id/full` | Paciente con historia completa | Sí |

#### Historia Médica

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/patients/:id/history` | Obtener historia médica | Sí |
| `POST` | `/patients/:id/history` | Crear/actualizar historia | Sí (Médico) |
| `PUT` | `/patients/:id/history` | Modificar historia | Sí (Médico) |

#### Notas Clínicas

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/patients/:id/notes` | Listar notas del paciente | Sí |
| `POST` | `/notes` | Crear nota clínica | Sí (Médico) |
| `GET` | `/notes/:id` | Obtener nota por ID | Sí |
| `PUT` | `/notes/:id` | Actualizar nota | Sí (Médico) |
| `DELETE` | `/notes/:id` | Eliminar nota | Sí (Admin) |

---

## 📊 Modelos de Datos

### Patient (Paciente)

```python
{
    "patient_id": 1,
    "doc_type": "CEDULA",
    "doc_number": "1234567890",
    "first_name": "Juan",
    "last_name": "Pérez García",
    "email": "juan.perez@email.com",
    "phone": "0987654321",
    "gender": "M",
    "birth_date": "1985-03-15",
    "age": 40,
    "address": "Av. Principal 123, Quito",
    "emergency_contact": "María Pérez - 0998765432",
    "created_at": "2025-12-17T10:00:00Z"
}
```

| Campo | Tipo | Descripción | Validación |
|-------|------|-------------|------------|
| `patient_id` | int | ID único del paciente | PK, Autoincremental |
| `doc_type` | string | Tipo de documento | CEDULA, RUC, PASAPORTE |
| `doc_number` | string | Número de documento | Único, validación según tipo |
| `first_name` | string | Nombres | Requerido, max 100 |
| `last_name` | string | Apellidos | Requerido, max 100 |
| `email` | string | Email de contacto | Formato email válido |
| `phone` | string | Teléfono celular | 10 dígitos, inicia con 09 |
| `gender` | string | Género | M, F, Otro |
| `birth_date` | date | Fecha de nacimiento | Formato: YYYY-MM-DD |
| `age` | int | Edad calculada | Auto-calculado |
| `address` | text | Dirección completa | Opcional |
| `emergency_contact` | string | Contacto de emergencia | Nombre + teléfono |

### Medical History (Historia Médica)

```python
{
    "history_id": 1,
    "patient_id": 1,
    "allergies": "Penicilina, Polen",
    "pathologies": "Hipertensión arterial",
    "surgeries": "Apendicectomía (2010)",
    "medications": "Losartán 50mg 1 vez al día",
    "blood_type": "O+",
    "family_history": "Padre diabético tipo 2",
    "lifestyle": "No fumador, ejercicio 3x/semana",
    "created_at": "2025-12-17T10:00:00Z",
    "updated_at": "2025-12-17T15:30:00Z"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `history_id` | int | ID único de la historia |
| `patient_id` | int | ID del paciente (1 a 1) |
| `allergies` | text | Alergias conocidas |
| `pathologies` | text | Enfermedades crónicas |
| `surgeries` | text | Cirugías previas |
| `medications` | text | Medicamentos actuales |
| `blood_type` | string | Tipo de sangre (A+, A-, B+, O-, AB+, etc.) |
| `family_history` | text | Antecedentes familiares |
| `lifestyle` | text | Hábitos y estilo de vida |

### Clinical Note (Nota Clínica)

```python
{
    "note_id": 1,
    "appointment_id": 5,
    "patient_id": 1,
    "doctor_id": 2,
    "observations": "Paciente refiere dolor en región lumbar desde hace 3 días",
    "diagnosis": "Lumbalgia mecánica",
    "treatment": "Ibuprofeno 400mg cada 8h x 5 días, reposo relativo",
    "created_at": "2025-12-17T10:00:00Z"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `note_id` | int | ID único de la nota |
| `appointment_id` | int | ID de la cita asociada |
| `patient_id` | int | ID del paciente |
| `doctor_id` | int | ID del médico que atendió |
| `observations` | text | Observaciones y motivo de consulta |
| `diagnosis` | text | Diagnóstico médico |
| `treatment` | text | Tratamiento prescrito |
| `created_at` | timestamp | Fecha de creación |

---

## 🇪🇨 Normativa Ecuador

### Validación de Cédula Ecuatoriana

El servicio implementa el algoritmo de validación de cédula ecuatoriana con dígito verificador:

```python
def validar_cedula(cedula: str) -> bool:
    """
    Valida cédula ecuatoriana de 10 dígitos
    - Primeros 2 dígitos: provincia (01-24)
    - Tercer dígito: sector (0-6)
    - Últimos 10 dígitos: código + verificador
    """
    # Implementación del algoritmo módulo 10
```

### Validación de RUC

```python
def validar_ruc(ruc: str) -> bool:
    """
    Valida RUC ecuatoriano de 13 dígitos
    - Primeros 10: cédula válida
    - Últimos 3: establecimiento (001-999)
    """
```

### Tipos de Documentos Aceptados

| Tipo | Formato | Validación |
|------|---------|------------|
| CEDULA | 10 dígitos | Algoritmo módulo 10 |
| RUC | 13 dígitos | Cédula + establecimiento |
| PASAPORTE | Alfanumérico | Formato libre |

---

## 🚀 Instalación

### Instalar Dependencias

```bash
cd backend/historia_clinica_service
pip install -r ../requirements-base.txt
```

### Variables de Entorno

```env
DATABASE_URL=postgresql://user:password@localhost:5432/clinica_db
JWT_SECRET_KEY=tu_clave_secreta
```

### Migrar Base de Datos

```bash
cd backend
alembic upgrade head
```

---

## 💻 Uso

### Ejecutar el Servicio

```bash
cd backend/historia_clinica_service
python app.py
```

El servicio estará disponible en `http://localhost:5003`

### Ejemplo de Creación de Paciente

```bash
curl -X POST http://localhost:5003/api/historia-clinica/patients \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "doc_type": "CEDULA",
    "doc_number": "1234567890",
    "first_name": "Juan",
    "last_name": "Pérez García",
    "email": "juan.perez@email.com",
    "phone": "0987654321",
    "gender": "M",
    "birth_date": "1985-03-15",
    "address": "Av. Principal 123, Quito"
  }'
```

### Ejemplo de Búsqueda de Paciente

```bash
# Buscar por nombre
curl -X GET "http://localhost:5003/api/historia-clinica/patients/search?q=Juan" \
  -H "Authorization: Bearer TOKEN"

# Buscar por cédula
curl -X GET "http://localhost:5003/api/historia-clinica/patients/search?doc_number=1234567890" \
  -H "Authorization: Bearer TOKEN"
```

### Ejemplo de Creación de Nota Clínica

```bash
curl -X POST http://localhost:5003/api/historia-clinica/notes \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "appointment_id": 5,
    "patient_id": 1,
    "observations": "Paciente refiere dolor en región lumbar",
    "diagnosis": "Lumbalgia mecánica",
    "treatment": "Ibuprofeno 400mg c/8h x 5 días"
  }'
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
cd backend
pytest tests/test_historia_clinica.py -v
```

### Casos de Prueba

- ✅ Validación de cédula ecuatoriana
- ✅ Validación de RUC
- ✅ CRUD de pacientes
- ✅ Búsqueda de pacientes
- ✅ Creación de historia médica
- ✅ Registro de notas clínicas
- ✅ Cálculo automático de edad
- ✅ Validación de email y teléfono

---

## 🔒 Privacidad y Seguridad

### LOPD - Ley de Protección de Datos

- ✅ Datos sensibles encriptados en tránsito (HTTPS)
- ✅ Acceso restringido por roles
- ✅ Auditoría de accesos
- ✅ Consentimiento informado del paciente

### Control de Acceso

- **Admin**: Acceso completo
- **Médico**: Lectura/escritura de historia y notas
- **Recepcionista**: Lectura de datos demográficos, creación de pacientes

---

## 🔗 Integración con Otros Servicios

### Citas Service
- Vinculación de notas clínicas con citas
- Historial de atenciones por paciente

### Facturación Service
- Datos del paciente para facturas
- Validación de cédula/RUC para SRI

---

## 🐛 Troubleshooting

### Error: "Invalid cedula format"
- Verifica que la cédula tenga 10 dígitos
- Usa el algoritmo de validación

### Error: "Patient already exists"
- El `doc_number` debe ser único
- Verifica si el paciente ya está registrado

### Error: "Invalid birth_date"
- Formato debe ser: YYYY-MM-DD
- La edad debe ser realista (0-120 años)

---

## 📚 Recursos Adicionales

- **Swagger UI**: http://localhost:5003/docs
- **Documentación General**: [../../README.md](../../README.md)
- **Esquema de BD**: [../../docs/ESQUEMA_BASE_DATOS.md](../../docs/ESQUEMA_BASE_DATOS.md)

---

**Última actualización:** 2025-12-17
