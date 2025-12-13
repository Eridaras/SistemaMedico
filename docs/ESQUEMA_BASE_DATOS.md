# 🗄️ Esquema de Base de Datos - Sistema Médico

Este documento detalla la estructura de la base de datos PostgreSQL, incluyendo diagramas de relaciones y descripciones de tablas.

---

## 📊 Diagrama Entidad-Relación (ERD)

```mermaid
erDiagram
    %% AUTH SERVICE
    ROLES ||--|{ USERS : "assigned to"
    ROLES {
        int role_id PK
        string name
        json menu_config
    }
    USERS {
        int user_id PK
        int role_id FK
        string email
        string password_hash
        string full_name
        boolean is_active
    }

    %% HISTORIA CLINICA SERVICE
    PATIENTS ||--o| MEDICAL_HISTORY : "has"
    PATIENTS ||--o{ APPOINTMENTS : "books"
    PATIENTS {
        int patient_id PK
        string doc_type
        string doc_number
        string first_name
        string last_name
        string email
        string phone
        string gender
        date birth_date
    }
    MEDICAL_HISTORY {
        int history_id PK
        int patient_id FK
        text allergies
        text pathologies
        text surgeries
        string blood_type
    }
    CLINICAL_NOTES {
        int note_id PK
        int appointment_id FK
        text observations
        text diagnosis
    }

    %% CITAS SERVICE
    USERS ||--o{ APPOINTMENTS : "doctor manages"
    APPOINTMENTS ||--o{ CLINICAL_NOTES : "generates"
    APPOINTMENTS {
        int appointment_id PK
        int patient_id FK
        int doctor_id FK
        datetime start_time
        datetime end_time
        string status
        string reason
    }

    %% INVENTARIO SERVICE
    PRODUCTS ||--o{ INVOICE_ITEMS : "included in"
    PRODUCTS {
        int product_id PK
        string sku
        string name
        decimal cost_price
        decimal sale_price
        int stock_quantity
        int min_stock_alert
    }
    TREATMENTS ||--o{ TREATMENT_RECIPES : "composed of"
    TREATMENTS {
        int treatment_id PK
        string name
        decimal base_price
    }
    TREATMENT_RECIPES {
        int recipe_id PK
        int treatment_id FK
        int product_id FK
        int quantity_needed
    }
    PRODUCTS ||--o{ TREATMENT_RECIPES : "used in"

    %% FACTURACION SERVICE
    PATIENTS ||--o{ INVOICES : "billed to"
    INVOICES ||--|{ INVOICE_ITEMS : "contains"
    INVOICES {
        int invoice_id PK
        int patient_id FK
        string clave_acceso
        string estado_sri
        decimal subtotal
        decimal total
        datetime created_at
    }
    INVOICE_ITEMS {
        int item_id PK
        int invoice_id FK
        int product_id FK
        int quantity
        decimal unit_price
        decimal total_price
    }
    SRI_CONFIGURATION {
        int config_id PK
        string ruc_emisor
        string razon_social
        string ambiente
        bytea p12_certificate
    }
```

---

## 📚 Diccionario de Datos Detallado

### 1. Módulo de Autenticación (`auth_service`)

| Tabla | Descripción | Columnas Clave |
|-------|-------------|----------------|
| **`roles`** | Define los perfiles de acceso (Admin, Médico, Recepción). | `menu_config`: JSON con permisos de UI. |
| **`users`** | Usuarios del sistema. El `role_id` define sus permisos. | `full_name`: Nombre visible en sidebar. |

### 2. Módulo de Historia Clínica (`historia_clinica_service`)

| Tabla | Descripción | Columnas Clave |
|-------|-------------|----------------|
| **`patients`** | Información demográfica. | `doc_number`: Identificador único (Cédula/RUC). |
| **`medical_history`** | Antecedentes médicos (1 a 1 con Paciente). | `allergies`, `blood_type`. |
| **`clinical_notes`** | Notas de evolución asociadas a una cita. | `diagnosis`: Diagnóstico médico. |

### 3. Módulo de Citas (`citas_service`)

| Tabla | Descripción | Columnas Clave |
|-------|-------------|----------------|
| **`appointments`** | Agenda médica. Relaciona Paciente y Doctor. | `status`: (PENDING, CONFIRMED, COMPLETED, CANCELLED). |

### 4. Módulo de Inventario (`inventario_service`)

| Tabla | Descripción | Columnas Clave |
|-------|-------------|----------------|
| **`products`** | Ítems físicos (medicamentos, insumos). | `min_stock_alert`: Umbral para alertas. `sku`: Código único. |
| **`treatments`** | Servicios médicos ofrecidos. | `base_price`: Precio base del servicio. |
| **`treatment_recipes`** | Receta de insumos para un tratamiento. | Permite descontar stock automáticamente al realizar un tratamiento. |

### 5. Módulo de Facturación (`facturacion_service`)

| Tabla | Descripción | Columnas Clave |
|-------|-------------|----------------|
| **`invoices`** | Cabecera de facturas electrónicas. | `clave_acceso`: 49 dígitos SRI. `estado_sri`: Estado de autorización. |
| **`invoice_items`** | Detalle de productos/servicios facturados. | Relacionado con `products`. |
| **`sri_configuration`** | Configuración del emisor y certificados. | Almacena el `.p12` y credenciales. |

---

## 🔗 Relaciones Críticas de Microservicios

Aunque los servicios son independientes, comparten la base de datos PostgreSQL (en el esquema actual monolítico de BD) lo que permite integridad referencial fuerte:

1.  **Facturación -> Inventario**: `invoice_items` referencia a `products` para obtener precios y nombres.
2.  **Citas -> Usuarios**: `appointments` referencia a `users` (Doctores).
3.  **Citas -> Historia**: `clinical_notes` se crea a partir de una `appointment` completada.

## 📝 Notas de Implementación

-   **Integridad**: Todas las claves foráneas (`FK`) tienen restricciones `ON DELETE RESTRICT` o `CASCADE` según corresponda.
-   **Auditoría**: Casi todas las tablas incluyen `created_at` (timestamp con zona horaria).
-   **JSONB**: Usado en `roles.menu_config` para flexibilidad en la configuración de la UI.
