"""
Swagger configuration for Auth Service
"""
from flask_restx import Api

authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"'
    }
}

api = Api(
    version='1.0',
    title='Auth Service API',
    description='Microservicio de Autenticación y Gestión de Usuarios',
    doc='/docs',
    authorizations=authorizations,
    security='Bearer'
)
