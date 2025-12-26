# 🔒 Security Policy - Sistema Médico

## Política de Seguridad

Este documento describe las políticas de seguridad y el proceso para reportar vulnerabilidades en el Sistema Médico de Clínica Bienestar.

---

## 📋 Índice

- [Versiones Soportadas](#-versiones-soportadas)
- [Reportar una Vulnerabilidad](#-reportar-una-vulnerabilidad)
- [Mejores Prácticas](#-mejores-prácticas)
- [Configuración de Seguridad](#-configuración-de-seguridad)
- [Auditorías de Seguridad](#-auditorías-de-seguridad)

---

## 🛡️ Versiones Soportadas

Actualmente estamos dando soporte de seguridad a las siguientes versiones:

| Versión | Soportada          | Notas                    |
| ------- | ------------------ | ------------------------ |
| 1.1.x   | :white_check_mark: | Versión actual estable   |
| 1.0.x   | :x:                | Actualizar a 1.1.x       |
| < 1.0   | :x:                | No soportado             |

---

## 🚨 Reportar una Vulnerabilidad

### Proceso de Reporte

Si descubres una vulnerabilidad de seguridad, por favor **NO** la publiques públicamente. Sigue estos pasos:

1. **Contacto Directo**
   - Email: security@clinicabienestar.com
   - Asunto: `[SECURITY] Descripción breve`

2. **Información Requerida**
   - Descripción detallada de la vulnerabilidad
   - Pasos para reproducir el problema
   - Impacto potencial
   - Versión afectada
   - Propuesta de solución (si aplica)

3. **Tiempos de Respuesta**
   - Acuse de recibo: **24 horas**
   - Evaluación inicial: **72 horas**
   - Plan de remediación: **7 días**
   - Fix y release: **30 días** (según severidad)

### Severidad de Vulnerabilidades

| Nivel | Descripción | Tiempo de Respuesta |
|-------|-------------|---------------------|
| **CRÍTICO** | Acceso no autorizado a datos de pacientes, ejecución remota de código | 24-48 horas |
| **ALTO** | Escalación de privilegios, inyección SQL, XSS almacenado | 3-7 días |
| **MEDIO** | XSS reflejado, CSRF, divulgación de información | 7-14 días |
| **BAJO** | Problemas de configuración, mejoras de seguridad | 14-30 días |

### Programa de Reconocimiento

Agradecemos a los investigadores de seguridad que reportan vulnerabilidades responsablemente:

- Reconocimiento público (si lo deseas)
- Inclusión en nuestro Hall of Fame de Seguridad
- Compensación según severidad (a discreción del equipo)

---

## 🔐 Mejores Prácticas

### Para Desarrolladores

#### 1. Autenticación y Autorización

```python
# ✅ CORRECTO: Verificar JWT y roles
@app.route('/api/patients', methods=['GET'])
@token_required
@role_required(['Admin', 'Doctor'])
def get_patients(current_user):
    return jsonify(patients)

# ❌ INCORRECTO: Sin verificación
@app.route('/api/patients', methods=['GET'])
def get_patients():
    return jsonify(patients)
```

#### 2. Validación de Entrada

```python
# ✅ CORRECTO: Usar Pydantic
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

# ❌ INCORRECTO: Sin validación
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(**data)  # Peligroso!
```

#### 3. Prevención de SQL Injection

```python
# ✅ CORRECTO: Usar ORM o prepared statements
user = db.session.query(User).filter_by(email=email).first()

# ❌ INCORRECTO: Concatenación de strings
query = f"SELECT * FROM users WHERE email = '{email}'"  # Peligroso!
```

#### 4. Manejo de Contraseñas

```python
# ✅ CORRECTO: Hash con bcrypt
import bcrypt
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))

# ❌ INCORRECTO: Almacenar en texto plano
user.password = password  # NUNCA HACER ESTO!
```

#### 5. Prevención de XSS

```javascript
// ✅ CORRECTO: Escapar HTML
const sanitized = DOMPurify.sanitize(userInput);

// ❌ INCORRECTO: Insertar directamente
element.innerHTML = userInput;  // Peligroso!
```

### Para Administradores

#### 1. Variables de Entorno

```bash
# ✅ CORRECTO: Usar variables de entorno
JWT_SECRET_KEY=$(openssl rand -hex 32)

# ❌ INCORRECTO: Hardcodear en código
JWT_SECRET_KEY = "supersecret123"  # NUNCA!
```

#### 2. Permisos de Archivos

```bash
# ✅ CORRECTO: Permisos restrictivos
chmod 600 .env
chmod 600 backend/storage/certificates/*.p12

# ❌ INCORRECTO: Permisos abiertos
chmod 777 .env  # Peligroso!
```

#### 3. Actualizaciones de Seguridad

```bash
# Actualizar dependencias regularmente
npm audit fix
pip-audit

# Revisar dependencias obsoletas
npm outdated
pip list --outdated
```

---

## ⚙️ Configuración de Seguridad

### Backend

#### 1. JWT Configuration

```python
# config.py
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')  # Mínimo 32 caracteres
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24
JWT_ISSUER = 'clinica-bienestar'
JWT_AUDIENCE = 'clinica-api'

# Validación estricta
jwt.decode(
    token,
    JWT_SECRET_KEY,
    algorithms=[JWT_ALGORITHM],
    options={
        'verify_signature': True,
        'verify_exp': True,
        'verify_iss': True,
        'verify_aud': True
    }
)
```

#### 2. CORS Configuration

```python
# app.py
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://clinicabienestar.com",
            "https://www.clinicabienestar.com"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Range", "X-Content-Range"],
        "supports_credentials": True,
        "max_age": 3600
    }
})
```

#### 3. Rate Limiting

```python
# app.py
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    storage_uri="redis://localhost:6379"
)

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    pass
```

#### 4. Security Headers

```python
# app.py
from flask_talisman import Talisman

Talisman(app,
    force_https=True,
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'"
    }
)
```

### Frontend

#### 1. Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=https://api.clinicabienestar.com  # Solo HTTPS en producción
```

#### 2. Content Security Policy

```typescript
// next.config.ts
const securityHeaders = [
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin'
  }
]
```

---

## 🔍 Auditorías de Seguridad

### Herramientas Automatizadas

#### Backend
```bash
# Escaneo de vulnerabilidades en dependencias
pip-audit

# Análisis estático de código
bandit -r backend/

# Linting de seguridad
ruff check --select S backend/
```

#### Frontend
```bash
# Auditoría de dependencias
npm audit

# Análisis de bundle
npm run build && npm run analyze
```

### Checklist de Seguridad

#### Desarrollo
- [ ] No hay credenciales hardcodeadas en el código
- [ ] Todas las contraseñas usan bcrypt con al menos 12 rounds
- [ ] JWT tiene secret robusto (min 32 caracteres)
- [ ] Todas las rutas protegidas usan `@token_required`
- [ ] Input validation con Pydantic en todos los endpoints
- [ ] No hay queries SQL concatenadas (usar ORM)
- [ ] CORS configurado restrictivamente
- [ ] Rate limiting en endpoints críticos
- [ ] Logs no contienen información sensible

#### Deployment
- [ ] HTTPS habilitado (SSL/TLS)
- [ ] Variables de entorno en `.env` (no en código)
- [ ] Permisos de archivos correctos (600 para .env)
- [ ] Firewall configurado (solo puertos necesarios)
- [ ] Backups automáticos configurados
- [ ] Logs centralizados y monitoreados
- [ ] Certificado SRI P12 encriptado
- [ ] PostgreSQL con contraseña fuerte
- [ ] Redis con contraseña (si aplica)

#### Producción
- [ ] Dependencias actualizadas
- [ ] Escaneo de vulnerabilidades pasado
- [ ] Penetration testing realizado
- [ ] Plan de respuesta a incidentes documentado
- [ ] Contacto de seguridad publicado
- [ ] Backups probados y funcionales

---

## 🎯 Compliance

### Protección de Datos (LOPD Ecuador)

- **Consentimiento**: Obtener consentimiento explícito para datos de pacientes
- **Acceso**: Solo usuarios autorizados acceden a datos sensibles
- **Retención**: Logs retenidos por 90 días, datos médicos según ley
- **Portabilidad**: Capacidad de exportar datos del paciente
- **Derecho al Olvido**: Capacidad de eliminar datos (con restricciones legales)

### Estándares Médicos

- **HIPAA** (referencia internacional): Protección de información de salud
- **HL7**: Estándar de intercambio de información médica
- **SRI Ecuador**: Cumplimiento de normativa de facturación electrónica

---

## 📞 Contacto de Seguridad

- **Email**: security@clinicabienestar.com
- **PGP Key**: [Disponible bajo solicitud]
- **Tiempo de respuesta**: 24-48 horas

---

## 📚 Recursos Adicionales

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Improvement Plan](docs/IMPROVEMENT_PLAN.md)

---

**Última actualización:** 2025-12-17
**Próxima revisión:** 2026-03-17 (trimestral)
