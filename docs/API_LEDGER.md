# API LEDGER - Tabla de Rutas y Base de Datos

**Última Actualización:** 2025-12-24
**Estado:** 100+ endpoints documentados, 14 tablas PostgreSQL

---

## 📊 DATABASE SCHEMA (PostgreSQL 16)

### users
- **PK:** user_id (SERIAL)
- **Campos:** email (UNIQUE), password_hash, role_id (FK), full_name, is_active, created_at
- **Relaciones:** belongsTo roles
- **Índices:** idx_users_email

### roles
- **PK:** role_id (SERIAL)
- **Campos:** name (VARCHAR), menu_config (JSONB)
- **Relaciones:** hasMany users

### patients
- **PK:** patient_id (SERIAL)
- **Campos:** doc_type, doc_number (UNIQUE), first_name, last_name, email, phone, address, birth_date, gender, created_at
- **Relaciones:** hasMany appointments, medical_history, invoices
- **Índices:** idx_patients_doc_number

### medical_history
- **PK:** history_id (SERIAL)
- **Campos:** patient_id (FK UNIQUE), allergies (TEXT), pathologies (TEXT), surgeries (TEXT), family_history (TEXT), blood_type
- **Relaciones:** belongsTo patients

### clinical_notes
- **PK:** note_id (SERIAL)
- **Campos:** appointment_id (FK), observations (TEXT), diagnosis (TEXT), created_at
- **Relaciones:** belongsTo appointments

### products
- **PK:** product_id (SERIAL)
- **Campos:** sku (UNIQUE), name, description, cost_price, sale_price, stock_quantity, min_stock_alert, is_active
- **Relaciones:** hasMany treatment_recipes, appointment_extras

### treatments
- **PK:** treatment_id (SERIAL)
- **Campos:** name, category, base_price, description, is_active
- **Relaciones:** hasMany treatment_recipes, appointment_treatments

### treatment_recipes
- **PK:** recipe_id (SERIAL)
- **Campos:** treatment_id (FK), product_id (FK), quantity_needed
- **Relaciones:** belongsTo treatments, products

### appointments
- **PK:** appointment_id (SERIAL)
- **Campos:** patient_id (FK), doctor_id (FK users), start_time, end_time, status, reason, created_at
- **Relaciones:** belongsTo patients, users; hasMany clinical_notes, appointment_treatments, appointment_extras
- **Índices:** idx_appointments_dates, idx_appointments_doctor

### appointment_treatments
- **PK:** detail_id (SERIAL)
- **Campos:** appointment_id (FK), treatment_id (FK), price_at_moment, quantity

### appointment_extras
- **PK:** extra_id (SERIAL)
- **Campos:** appointment_id (FK), product_id (FK), quantity, price_charged

### invoices
- **PK:** invoice_id (SERIAL)
- **Campos:** patient_id (FK), appointment_id (FK), invoice_number (UNIQUE), issue_date, subtotal, iva_rate, iva_amount, total_amount, status
- **Índices:** idx_invoices_dates

### operational_expenses
- **PK:** expense_id (SERIAL)
- **Campos:** description, amount, expense_date, category, registered_by (FK users)

### electronic_invoices
- **PK:** electronic_invoice_id (SERIAL)
- **Campos:** invoice_id (FK), authorization_number, issue_date, xml_signed (TEXT), access_key, status, sri_response (JSONB)

### system_logs
- **PK:** log_id (SERIAL)
- **Campos:** service_name, action, user_id (FK), details (TEXT), level, ip_address, created_at
- **Índices:** idx_logs_service_level

---

## 🌐 API ENDPOINTS

### AUTH SERVICE (:5001) - `/api/auth`

| Método | Ruta | Auth | Input | Output | Controller |
|--------|------|------|-------|--------|------------|
| POST | `/login` | No | `{email, password}` | `{token, user}` | auth_bp.login |
| POST | `/register` | No | `{email, password, full_name, role_id?}` | `{token, user}` | auth_bp.register |
| GET | `/me` | Bearer | - | `{user}` | auth_bp.get_current_user |
| GET | `/users` | Bearer | `?page=1&per_page=20` | `{users[], pagination}` | auth_bp.list_users |
| GET | `/roles` | Bearer | - | `{roles[]}` | auth_bp.list_roles |
| POST | `/roles` | Bearer | `{name, menu_config}` | `{role}` | auth_bp.create_role |
| PUT | `/roles/:id` | Bearer | `{name?, menu_config?}` | `{role}` | auth_bp.update_role |
| GET | `/validate` | Bearer | - | `{valid: true, user}` | auth_bp.validate_token |
| GET | `/health` | No | - | `{status: 'healthy'}` | auth_bp.health_check |

### INVENTARIO SERVICE (:5002) - `/api/inventario`

| Método | Ruta | Auth | Input | Output | Controller |
|--------|------|------|-------|--------|------------|
| GET | `/products` | Bearer | `?page=1&search=...&low_stock=true` | `{products[], pagination}` | inventario_bp.list_products |
| GET | `/products/:id` | Bearer | - | `{product}` | inventario_bp.get_product |
| POST | `/products` | Bearer | `{name, sku?, cost_price, sale_price, stock_quantity?, min_stock_alert?}` | `{product}` | inventario_bp.create_product |
| PUT | `/products/:id` | Bearer | `{name?, cost_price?, ...}` | `{product}` | inventario_bp.update_product |
| PATCH | `/products/:id/stock` | Bearer | `{quantity_change}` | `{product}` | inventario_bp.update_stock |
| GET | `/products/low-stock` | Bearer | - | `{products[], count}` | inventario_bp.get_low_stock |
| GET | `/treatments` | Bearer | `?page=1&search=...&category=...` | `{treatments[], pagination}` | inventario_bp.list_treatments |
| GET | `/treatments/:id` | Bearer | - | `{treatment, recipe[], cost, margin}` | inventario_bp.get_treatment |
| POST | `/treatments` | Bearer | `{name, base_price, category?, description?}` | `{treatment}` | inventario_bp.create_treatment |
| PUT | `/treatments/:id` | Bearer | `{name?, base_price?, ...}` | `{treatment}` | inventario_bp.update_treatment |
| GET | `/treatments/categories` | Bearer | - | `{categories[]}` | inventario_bp.get_categories |
| GET | `/treatments/:id/recipe` | Bearer | - | `{recipe[], total_cost}` | inventario_bp.get_recipe |
| POST | `/treatments/:id/recipe` | Bearer | `{product_id, quantity_needed}` | `{ingredient}` | inventario_bp.add_ingredient |
| DELETE | `/treatments/:id/recipe/:product_id` | Bearer | - | `{message}` | inventario_bp.remove_ingredient |
| GET | `/treatments/:id/check-stock` | Bearer | `?quantity=1` | `{all_available, items[]}` | inventario_bp.check_stock |
| GET | `/health` | No | - | `{status: 'healthy'}` | inventario_bp.health_check |

### HISTORIA CLINICA SERVICE (:5003) - `/api/historia-clinica`

| Método | Ruta | Auth | Input | Output | Controller |
|--------|------|------|-------|--------|------------|
| GET | `/patients` | Bearer | `?page=1&search=...` | `{patients[], pagination}` | historia_clinica_bp.list_patients |
| GET | `/patients/:id` | Bearer | - | `{patient, medical_history, recent_appointments[]}` | historia_clinica_bp.get_patient |
| POST | `/patients` | Bearer | `{doc_type, doc_number, first_name, last_name, email?, phone?, birth_date?, gender?}` | `{patient}` | historia_clinica_bp.create_patient |
| PUT | `/patients/:id` | Bearer | `{first_name?, last_name?, ...}` | `{patient}` | historia_clinica_bp.update_patient |
| GET | `/patients/search` | Bearer | `?doc_number=...` | `{patient}` | historia_clinica_bp.search_patients |
| GET | `/patients/:id/medical-history` | Bearer | - | `{medical_history}` | historia_clinica_bp.get_medical_history |
| POST | `/patients/:id/medical-history` | Bearer | `{allergies?, pathologies?, surgeries?, family_history?, blood_type?}` | `{medical_history}` | historia_clinica_bp.create_or_update_medical_history |
| PUT | `/patients/:id/medical-history` | Bearer | `{allergies?, ...}` | `{medical_history}` | historia_clinica_bp.update_medical_history |
| GET | `/patients/:id/notes` | Bearer | `?page=1` | `{notes[]}` | historia_clinica_bp.get_patient_notes |
| GET | `/notes/:id` | Bearer | - | `{note}` | historia_clinica_bp.get_note |
| GET | `/appointments/:id/notes` | Bearer | - | `{notes[]}` | historia_clinica_bp.get_appointment_notes |
| POST | `/appointments/:id/notes` | Bearer | `{observations, diagnosis?}` | `{note}` | historia_clinica_bp.create_note |
| PUT | `/notes/:id` | Bearer | `{observations?, diagnosis?}` | `{note}` | historia_clinica_bp.update_note |
| GET | `/health` | No | - | `{status: 'healthy'}` | historia_clinica_bp.health_check |

### FACTURACION SERVICE (:5004) - `/api/facturacion`

| Método | Ruta | Auth | Input | Output | Controller |
|--------|------|------|-------|--------|------------|
| GET | `/invoices` | Bearer | `?page=1&status=...&date_from=...&date_to=...` | `{invoices[], pagination}` | facturacion_bp.list_invoices |
| GET | `/invoices/:id` | Bearer | - | `{invoice}` | facturacion_bp.get_invoice |
| POST | `/invoices` | Bearer | `{patient_id, subtotal, appointment_id?, iva_rate?, status?}` | `{invoice}` | facturacion_bp.create_invoice |
| PUT | `/invoices/:id` | Bearer | `{subtotal?, iva_rate?, ...}` | `{invoice}` | facturacion_bp.update_invoice |
| PATCH | `/invoices/:id/status` | Bearer | `{status}` | `{invoice}` | facturacion_bp.update_invoice_status |
| GET | `/invoices/totals` | Bearer | `?date_from=...&date_to=...` | `{totals[]}` | facturacion_bp.get_invoice_totals |
| GET | `/expenses` | Bearer | `?page=1&category=...&date_from=...` | `{expenses[], pagination}` | facturacion_bp.list_expenses |
| GET | `/expenses/:id` | Bearer | - | `{expense}` | facturacion_bp.get_expense |
| POST | `/expenses` | Bearer | `{description, amount, expense_date?, category?}` | `{expense}` | facturacion_bp.create_expense |
| PUT | `/expenses/:id` | Bearer | `{description?, amount?, ...}` | `{expense}` | facturacion_bp.update_expense |
| DELETE | `/expenses/:id` | Bearer | - | `{message}` | facturacion_bp.delete_expense |
| GET | `/expenses/categories` | Bearer | - | `{categories[]}` | facturacion_bp.get_expense_categories |
| GET | `/expenses/totals` | Bearer | `?date_from=...&date_to=...` | `{totals[]}` | facturacion_bp.get_expense_totals |
| GET | `/reports/dashboard` | Bearer | `?date_from=...&date_to=...` | `{metrics{total_income, total_expenses, profit, ...}}` | facturacion_bp.get_dashboard_metrics |
| GET | `/health` | No | - | `{status: 'healthy'}` | facturacion_bp.health_check |

### CITAS SERVICE (:5005) - `/api/citas`

| Método | Ruta | Auth | Input | Output | Controller |
|--------|------|------|-------|--------|------------|
| GET | `/appointments` | Bearer | `?page=1&patient_id=...&doctor_id=...&status=...&date_from=...` | `{appointments[], pagination}` | citas_bp.list_appointments |
| GET | `/appointments/:id` | Bearer | - | `{appointment, treatments[], extras[], total}` | citas_bp.get_appointment |
| POST | `/appointments` | Bearer | `{patient_id, doctor_id, start_time, end_time, reason?, status?}` | `{appointment}` | citas_bp.create_appointment |
| PUT | `/appointments/:id` | Bearer | `{start_time?, end_time?, ...}` | `{appointment}` | citas_bp.update_appointment |
| PATCH | `/appointments/:id/status` | Bearer | `{status}` | `{appointment}` | citas_bp.update_appointment_status |
| POST | `/appointments/check-availability` | Bearer | `{doctor_id, start_time, end_time, exclude_appointment_id?}` | `{available: boolean}` | citas_bp.check_availability |
| GET | `/doctors/:id/schedule` | Bearer | `?date=YYYY-MM-DD` | `{schedule[], date, doctor_id}` | citas_bp.get_doctor_schedule |
| GET | `/appointments/:id/treatments` | Bearer | - | `{treatments[], total}` | citas_bp.get_appointment_treatments |
| POST | `/appointments/:id/treatments` | Bearer | `{treatment_id, price_at_moment, quantity?}` | `{treatment}` | citas_bp.add_treatment |
| PUT | `/appointments/treatments/:detail_id` | Bearer | `{price_at_moment?, quantity?}` | `{treatment}` | citas_bp.update_treatment |
| DELETE | `/appointments/treatments/:detail_id` | Bearer | - | `{message}` | citas_bp.remove_treatment |
| GET | `/appointments/:id/extras` | Bearer | - | `{extras[], total}` | citas_bp.get_appointment_extras |
| POST | `/appointments/:id/extras` | Bearer | `{product_id, quantity, price_charged?}` | `{extra}` | citas_bp.add_extra |
| PUT | `/appointments/extras/:extra_id` | Bearer | `{quantity?, price_charged?}` | `{extra}` | citas_bp.update_extra |
| DELETE | `/appointments/extras/:extra_id` | Bearer | - | `{message}` | citas_bp.remove_extra |
| GET | `/health` | No | - | `{status: 'healthy'}` | citas_bp.health_check |

### LOGS SERVICE (:5006) - `/api/logs`

| Método | Ruta | Auth | Input | Output | Controller |
|--------|------|------|-------|--------|------------|
| POST | `/logs` | No | `{service_name, action, user_id?, details?, level?, ip_address?}` | `{log}` | logs_bp.create_log |
| GET | `/logs` | Bearer | `?page=1&service_name=...&level=...&user_id=...&start_date=...&end_date=...` | `{logs[], pagination}` | logs_bp.list_logs |
| GET | `/logs/:id` | Bearer | - | `{log}` | logs_bp.get_log |
| GET | `/logs/stats` | Bearer | - | `{stats{total, by_service[], by_level[], recent_errors[]}}` | logs_bp.get_stats |
| POST | `/logs/cleanup` | Bearer | `{days?}` | `{deleted_count}` | logs_bp.cleanup_logs |
| GET | `/health` | No | - | `{status: 'healthy'}` | logs_bp.health_check |

---

## 🔐 AUTENTICACIÓN

### JWT Token Structure
```json
{
  "user_id": 1,
  "role_id": 1,
  "email": "user@example.com",
  "iss": "dental-clinic-api",
  "aud": "dental-clinic-app",
  "iat": 1234567890,
  "exp": 1234654290
}
```

### Headers Required
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

---

**Total Endpoints:** 100+
**Total Tablas:** 14
**Índices:** 6
