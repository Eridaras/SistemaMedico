# 🤝 Guía de Contribución - Sistema Médico

¡Gracias por tu interés en contribuir al Sistema Médico de Clínica Bienestar! Este documento te guiará a través del proceso de contribución.

---

## 📋 Índice

- [Código de Conducta](#-código-de-conducta)
- [Cómo Contribuir](#-cómo-contribuir)
- [Estándares de Código](#-estándares-de-código)
- [Proceso de Pull Request](#-proceso-de-pull-request)
- [Reportar Bugs](#-reportar-bugs)
- [Sugerir Features](#-sugerir-features)

---

## 📜 Código de Conducta

### Nuestros Valores

- **Respeto**: Trata a todos con respeto y profesionalismo
- **Inclusión**: Crea un ambiente acogedor para todos
- **Colaboración**: Trabaja en equipo y comparte conocimiento
- **Excelencia**: Mantén altos estándares de calidad

### Comportamiento Esperado

- Usa lenguaje acogedor e inclusivo
- Sé respetuoso con diferentes puntos de vista
- Acepta críticas constructivas con gracia
- Enfócate en lo que es mejor para la comunidad

### Comportamiento Inaceptable

- Comentarios ofensivos o discriminatorios
- Acoso público o privado
- Publicar información privada sin permiso
- Conducta poco profesional

---

## 🚀 Cómo Contribuir

### 1. Fork del Repositorio

```bash
# Fork en GitHub
# Luego clonar tu fork
git clone https://github.com/TU_USUARIO/sistema-medico.git
cd sistema-medico
```

### 2. Configurar el Entorno

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
pip install -r requirements-base.txt
pip install -r requirements-dev.txt

# Frontend
cd Frontend
npm install
```

### 3. Crear una Rama

```bash
# Nomenclatura:
# feature/nombre-feature
# fix/nombre-bug
# docs/nombre-doc
# refactor/nombre-refactor

git checkout -b feature/nueva-funcionalidad
```

### 4. Hacer Cambios

- Sigue los [estándares de código](#-estándares-de-código)
- Escribe tests para nuevas funcionalidades
- Actualiza la documentación si es necesario

### 5. Commit de Cambios

```bash
# Formato de commit:
# tipo(scope): descripción breve
#
# Tipos: feat, fix, docs, style, refactor, test, chore
# Scope: módulo afectado (auth, inventory, billing, etc.)

git add .
git commit -m "feat(auth): agregar autenticación de dos factores"
```

**Ejemplos de buenos commits:**
```
feat(billing): integrar facturación electrónica con SRI
fix(appointments): corregir validación de disponibilidad de citas
docs(readme): actualizar guía de instalación
refactor(inventory): optimizar consulta de productos con stock bajo
test(auth): agregar tests para renovación de token JWT
chore(deps): actualizar Flask a 3.1.0
```

### 6. Push y Pull Request

```bash
git push origin feature/nueva-funcionalidad
```

Luego crea un Pull Request en GitHub.

---

## 💻 Estándares de Código

### Backend (Python)

#### Estilo de Código

- **PEP 8**: Seguir la guía de estilo de Python
- **Ruff**: Linter configurado (ver `.ruff.toml`)
- **MyPy**: Type hints obligatorios

```python
# ✅ CORRECTO
def get_patient_by_id(patient_id: int) -> Optional[Patient]:
    """
    Obtiene un paciente por su ID.

    Args:
        patient_id: ID del paciente a buscar

    Returns:
        Objeto Patient si se encuentra, None si no existe

    Raises:
        ValueError: Si patient_id no es válido
    """
    if patient_id <= 0:
        raise ValueError("patient_id must be positive")

    return db.session.query(Patient).filter_by(id=patient_id).first()

# ❌ INCORRECTO
def get_patient(id):
    return db.session.query(Patient).filter_by(id=id).first()
```

#### Nombrado

```python
# Variables y funciones: snake_case
user_email = "user@example.com"
def calculate_total_price():
    pass

# Clases: PascalCase
class UserModel:
    pass

# Constantes: UPPER_CASE
MAX_LOGIN_ATTEMPTS = 5
JWT_EXPIRATION_HOURS = 24
```

#### Validación con Pydantic

```python
from pydantic import BaseModel, EmailStr, validator

class PatientCreate(BaseModel):
    doc_number: str
    first_name: str
    last_name: str
    email: EmailStr

    @validator('doc_number')
    def validate_cedula(cls, v):
        if not validate_cedula_ecuatoriana(v):
            raise ValueError('Invalid cedula')
        return v
```

#### Tests

```python
# tests/test_auth.py
import pytest

def test_login_success(client, test_user):
    """Test login with valid credentials"""
    response = client.post('/api/auth/login', json={
        'email': test_user.email,
        'password': 'password123'
    })

    assert response.status_code == 200
    assert 'token' in response.json['data']

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/api/auth/login', json={
        'email': 'wrong@example.com',
        'password': 'wrongpassword'
    })

    assert response.status_code == 401
```

### Frontend (TypeScript/React)

#### Estilo de Código

- **ESLint**: Configurado en `.eslintrc.json`
- **Prettier**: Formateo automático
- **TypeScript**: Types estrictos

```typescript
// ✅ CORRECTO
interface Patient {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
}

const getPatients = async (): Promise<Patient[]> => {
  const response = await fetch('/api/historia-clinica/patients');
  if (!response.ok) {
    throw new Error('Failed to fetch patients');
  }
  return response.json();
};

// ❌ INCORRECTO
const getPatients = async () => {
  const response = await fetch('/api/historia-clinica/patients');
  return response.json();
};
```

#### Componentes React

```typescript
// ✅ CORRECTO
interface PatientCardProps {
  patient: Patient;
  onEdit: (id: number) => void;
}

export const PatientCard: React.FC<PatientCardProps> = ({ patient, onEdit }) => {
  return (
    <div className="rounded-lg border p-4">
      <h3 className="text-lg font-semibold">{patient.firstName} {patient.lastName}</h3>
      <p className="text-sm text-gray-500">{patient.email}</p>
      <button onClick={() => onEdit(patient.id)}>
        Editar
      </button>
    </div>
  );
};

// ❌ INCORRECTO
export const PatientCard = (props) => {
  return (
    <div>
      <h3>{props.patient.firstName}</h3>
    </div>
  );
};
```

#### Hooks

```typescript
// ✅ CORRECTO
export const usePatients = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const data = await getPatients();
        setPatients(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPatients();
  }, []);

  return { patients, loading, error };
};
```

---

## 🔄 Proceso de Pull Request

### 1. Antes de Crear el PR

- [ ] El código pasa todos los tests
- [ ] El código sigue los estándares de estilo
- [ ] La documentación está actualizada
- [ ] Los commits siguen el formato especificado
- [ ] Has probado manualmente los cambios

```bash
# Backend
cd backend
pytest
ruff check .
mypy .

# Frontend
cd Frontend
npm run lint
npm run typecheck
npm run build
```

### 2. Crear el Pull Request

**Template de PR:**

```markdown
## Descripción
Describe qué hace este PR y por qué es necesario.

## Tipo de Cambio
- [ ] Bug fix (cambio que corrige un issue)
- [ ] Nueva feature (cambio que agrega funcionalidad)
- [ ] Breaking change (fix o feature que causa que funcionalidad existente no funcione)
- [ ] Documentación

## ¿Cómo se probó?
Describe las pruebas que realizaste.

## Checklist
- [ ] Mi código sigue los estándares del proyecto
- [ ] He realizado self-review de mi código
- [ ] He comentado mi código en áreas complejas
- [ ] He actualizado la documentación
- [ ] Mis cambios no generan nuevos warnings
- [ ] He agregado tests que prueban que mi fix funciona o que mi feature funciona
- [ ] Tests nuevos y existentes pasan localmente

## Screenshots (si aplica)
```

### 3. Proceso de Revisión

1. **Automated Checks**: CI/CD ejecuta tests y linters
2. **Code Review**: Al menos 1 aprobación requerida
3. **Discussion**: Responde a comentarios y sugerencias
4. **Update**: Realiza cambios solicitados
5. **Merge**: Una vez aprobado, se hace merge a main

### 4. Después del Merge

- Tu rama será eliminada
- Los cambios se desplegarán automáticamente (si aplica)
- Actualiza tu fork

```bash
git checkout main
git pull upstream main
git push origin main
```

---

## 🐛 Reportar Bugs

### Antes de Reportar

1. Busca si el bug ya fue reportado
2. Actualiza a la última versión
3. Verifica que sea un bug real (no una feature)

### Template de Bug Report

```markdown
**Descripción del Bug**
Descripción clara y concisa del bug.

**Pasos para Reproducir**
1. Ir a '...'
2. Click en '...'
3. Scroll hasta '...'
4. Ver error

**Comportamiento Esperado**
Qué esperabas que sucediera.

**Comportamiento Actual**
Qué sucedió en realidad.

**Screenshots**
Si aplica, agrega screenshots.

**Entorno:**
 - OS: [e.g. Windows 11, Ubuntu 22.04]
 - Browser: [e.g. Chrome 120, Firefox 121]
 - Versión: [e.g. 1.1.0]

**Logs**
```
Pega aquí los logs relevantes
```

**Contexto Adicional**
Cualquier otra información relevante.
```

---

## 💡 Sugerir Features

### Template de Feature Request

```markdown
**¿Está relacionado con un problema?**
Descripción clara del problema. Ej: "Siempre me frustra cuando..."

**Describe la solución que te gustaría**
Descripción clara de qué quieres que suceda.

**Describe alternativas que has considerado**
Descripción de soluciones o features alternativas.

**Contexto Adicional**
Cualquier otra información, screenshots, mockups, etc.

**Beneficios**
¿Por qué esta feature sería útil para la mayoría de usuarios?
```

---

## 🏆 Reconocimiento

Los contribuidores son reconocidos en:

- README.md (sección de Contribuidores)
- CHANGELOG.md (menciones en releases)
- Hall of Fame en la documentación

---

## 📞 Contacto

- **Email**: dev@clinicabienestar.com
- **GitHub Issues**: Para bugs y features
- **GitHub Discussions**: Para preguntas generales

---

## 📚 Recursos para Contribuidores

### Documentación Técnica
- [Arquitectura del Sistema](docs/ARCHITECTURE.md)
- [Esquema de Base de Datos](docs/ESQUEMA_BASE_DATOS.md)
- [Guía de Deployment](docs/DEPLOYMENT_GUIDE.md)
- [Estrategia de Pruebas](docs/ESTRATEGIA_PRUEBAS.md)

### Guías de Tecnologías
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Herramientas
- [Ruff](https://docs.astral.sh/ruff/) - Python linter
- [MyPy](https://mypy.readthedocs.io/) - Python type checker
- [ESLint](https://eslint.org/) - JavaScript linter
- [Prettier](https://prettier.io/) - Code formatter

---

**¡Gracias por contribuir! 🎉**

**Última actualización:** 2025-12-17
