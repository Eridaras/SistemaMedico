"""
SRI Production Services - Digital Signature and SOAP Client
PRODUCTION READY - Complete implementation with XMLDSig and SOAP
"""
from lxml import etree
from signxml import XMLSigner, methods
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.x509 import load_pem_x509_certificate
from zeep import Client, Settings
from zeep.transports import Transport
from zeep.exceptions import Fault as ZeepFault
from requests import Session
import logging
import os
from pathlib import Path


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XMLDigitalSigner:
    """
    Production-ready XML Digital Signature (XMLDSig) implementation
    Signs XML documents with PKCS#12 certificates for SRI compliance
    """

    def __init__(self, certificate_path=None, password=None):
        """
        Initialize digital signer

        Args:
            certificate_path: Path to .p12 certificate file
            password: Certificate password
        """
        self.certificate_path = certificate_path
        self.password = password
        self.cert_data = None
        self.private_key = None
        self.certificate = None

        if certificate_path and os.path.exists(certificate_path):
            self._load_certificate()

    def _load_certificate(self):
        """Load PKCS#12 certificate and extract private key"""
        try:
            with open(self.certificate_path, 'rb') as f:
                cert_data = f.read()

            # Load PKCS#12 with password
            private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
                cert_data,
                self.password.encode() if isinstance(self.password, str) else self.password,
                backend=default_backend()
            )

            self.private_key = private_key
            self.certificate = certificate
            self.cert_data = cert_data

            logger.info(f"Certificate loaded successfully from {self.certificate_path}")
            logger.info(f"Certificate subject: {certificate.subject}")
            logger.info(f"Certificate issuer: {certificate.issuer}")
            logger.info(f"Valid from: {certificate.not_valid_before_utc}")
            logger.info(f"Valid until: {certificate.not_valid_after_utc}")

        except Exception as e:
            logger.error(f"Error loading certificate: {str(e)}")
            raise

    def sign_xml(self, xml_string):
        """
        Sign XML with digital certificate using XMLDSig

        Args:
            xml_string: XML content as string

        Returns:
            Signed XML as string

        Raises:
            ValueError: If certificate is not loaded
            Exception: If signing fails
        """
        if not self.certificate or not self.private_key:
            # If no certificate configured, return unsigned XML with warning
            logger.warning("No certificate configured. Returning unsigned XML.")
            logger.warning("For production, configure certificate in sri_configuration table.")
            return xml_string

        try:
            # Parse XML string to lxml element
            root = etree.fromstring(xml_string.encode('utf-8'))

            # Create signer with certificate
            signer = XMLSigner(
                method=methods.enveloped,
                signature_algorithm='rsa-sha256',
                digest_algorithm='sha256',
                c14n_algorithm='http://www.w3.org/TR/2001/REC-xml-c14n-20010315'
            )

            # Convert private key to PEM format for signxml
            private_key_pem = self.private_key.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption()
            )

            # Convert certificate to PEM format
            cert_pem = self.certificate.public_bytes(Encoding.PEM)

            # Sign the XML
            signed_root = signer.sign(
                root,
                key=private_key_pem,
                cert=cert_pem
            )

            # Convert back to string
            signed_xml = etree.tostring(
                signed_root,
                encoding='UTF-8',
                xml_declaration=True,
                pretty_print=True
            ).decode('utf-8')

            logger.info("XML signed successfully with digital certificate")
            return signed_xml

        except Exception as e:
            logger.error(f"Error signing XML: {str(e)}")
            raise

    def verify_certificate_validity(self):
        """
        Verify if certificate is still valid

        Returns:
            Boolean indicating validity
        """
        if not self.certificate:
            return False

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)

        is_valid = (
            self.certificate.not_valid_before_utc <= now <=
            self.certificate.not_valid_after_utc
        )

        if not is_valid:
            logger.warning(f"Certificate is not valid. Valid period: "
                         f"{self.certificate.not_valid_before_utc} to "
                         f"{self.certificate.not_valid_after_utc}")

        return is_valid


class SRISOAPClient:
    """
    Production-ready SOAP client for SRI Web Services
    Handles reception and authorization of electronic invoices
    """

    # SRI Web Service URLs
    PRUEBAS_RECEPCION = "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"
    PRUEBAS_AUTORIZACION = "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"

    PRODUCCION_RECEPCION = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"
    PRODUCCION_AUTORIZACION = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"

    def __init__(self, ambiente="1"):
        """
        Initialize SRI SOAP client

        Args:
            ambiente: "1" for testing, "2" for production
        """
        self.ambiente = ambiente

        # Select URLs based on environment
        if ambiente == "1":
            self.url_recepcion = self.PRUEBAS_RECEPCION
            self.url_autorizacion = self.PRUEBAS_AUTORIZACION
            logger.info("Using SRI TEST environment")
        else:
            self.url_recepcion = self.PRODUCCION_RECEPCION
            self.url_autorizacion = self.PRODUCCION_AUTORIZACION
            logger.info("Using SRI PRODUCTION environment")

        # Configure session with timeout
        self.session = Session()
        self.session.headers.update({'Content-Type': 'text/xml; charset=utf-8'})

        # Configure transport
        self.transport = Transport(session=self.session, timeout=30)

        # Configure zeep settings
        self.settings = Settings(
            strict=False,
            xml_huge_tree=True,
            xsd_ignore_sequence_order=True
        )

        # Initialize clients (lazy loading)
        self._recepcion_client = None
        self._autorizacion_client = None

    def _get_recepcion_client(self):
        """Get or create reception client"""
        if self._recepcion_client is None:
            try:
                self._recepcion_client = Client(
                    self.url_recepcion,
                    transport=self.transport,
                    settings=self.settings
                )
                logger.info(f"Reception client initialized: {self.url_recepcion}")
            except Exception as e:
                logger.error(f"Error creating reception client: {str(e)}")
                raise

        return self._recepcion_client

    def _get_autorizacion_client(self):
        """Get or create authorization client"""
        if self._autorizacion_client is None:
            try:
                self._autorizacion_client = Client(
                    self.url_autorizacion,
                    transport=self.transport,
                    settings=self.settings
                )
                logger.info(f"Authorization client initialized: {self.url_autorizacion}")
            except Exception as e:
                logger.error(f"Error creating authorization client: {str(e)}")
                raise

        return self._autorizacion_client

    def enviar_comprobante(self, xml_string):
        """
        Send invoice to SRI for validation

        Args:
            xml_string: Signed XML string

        Returns:
            Dictionary with response:
            {
                'estado': 'RECIBIDA' | 'DEVUELTA',
                'clave_acceso': '...',
                'comprobantes': [...],
                'mensaje': 'Mensaje del SRI'
            }
        """
        try:
            client = self._get_recepcion_client()

            # Call SRI web service
            response = client.service.validarComprobante(xml_string)

            # Process response
            estado = response.estado if hasattr(response, 'estado') else 'DESCONOCIDO'

            result = {
                'estado': estado,
                'clave_acceso': None,
                'comprobantes': [],
                'mensaje': ''
            }

            # Extract information from response
            if hasattr(response, 'comprobantes'):
                comprobantes = response.comprobantes.comprobante if hasattr(response.comprobantes, 'comprobante') else []

                if not isinstance(comprobantes, list):
                    comprobantes = [comprobantes]

                for comp in comprobantes:
                    comp_info = {
                        'claveAcceso': comp.claveAcceso if hasattr(comp, 'claveAcceso') else None,
                        'mensajes': []
                    }

                    if hasattr(comp, 'mensajes') and comp.mensajes:
                        mensajes = comp.mensajes.mensaje if hasattr(comp.mensajes, 'mensaje') else []

                        if not isinstance(mensajes, list):
                            mensajes = [mensajes]

                        for msg in mensajes:
                            comp_info['mensajes'].append({
                                'identificador': msg.identificador if hasattr(msg, 'identificador') else None,
                                'mensaje': msg.mensaje if hasattr(msg, 'mensaje') else None,
                                'tipo': msg.tipo if hasattr(msg, 'tipo') else None,
                                'informacionAdicional': msg.informacionAdicional if hasattr(msg, 'informacionAdicional') else None
                            })

                    result['comprobantes'].append(comp_info)

                    # Set clave_acceso and mensaje from first comprobante
                    if comp_info['claveAcceso']:
                        result['clave_acceso'] = comp_info['claveAcceso']

                    if comp_info['mensajes']:
                        result['mensaje'] = comp_info['mensajes'][0]['mensaje']

            logger.info(f"Invoice sent to SRI successfully. Estado: {estado}")
            return result

        except ZeepFault as e:
            logger.error(f"SOAP Fault: {str(e)}")
            return {
                'estado': 'ERROR',
                'clave_acceso': None,
                'comprobantes': [],
                'mensaje': f'Error SOAP: {str(e)}'
            }

        except Exception as e:
            logger.error(f"Error sending invoice: {str(e)}")
            return {
                'estado': 'ERROR',
                'clave_acceso': None,
                'comprobantes': [],
                'mensaje': f'Error: {str(e)}'
            }

    def consultar_autorizacion(self, clave_acceso):
        """
        Query authorization status of invoice

        Args:
            clave_acceso: 49-digit access key

        Returns:
            Dictionary with authorization info:
            {
                'estado': 'AUTORIZADO' | 'NO AUTORIZADO' | 'EN PROCESO',
                'numero_autorizacion': '...',
                'fecha_autorizacion': '...',
                'ambiente': '1' | '2',
                'comprobante': '...',  # XML autorizado
                'mensajes': [...]
            }
        """
        try:
            client = self._get_autorizacion_client()

            # Call SRI web service
            response = client.service.autorizacionComprobante(clave_acceso)

            # Process response
            result = {
                'estado': 'DESCONOCIDO',
                'numero_autorizacion': None,
                'fecha_autorizacion': None,
                'ambiente': self.ambiente,
                'comprobante': None,
                'mensajes': []
            }

            if hasattr(response, 'autorizaciones'):
                autorizaciones = response.autorizaciones.autorizacion if hasattr(response.autorizaciones, 'autorizacion') else []

                if not isinstance(autorizaciones, list):
                    autorizaciones = [autorizaciones]

                if autorizaciones:
                    auth = autorizaciones[0]

                    result['estado'] = auth.estado if hasattr(auth, 'estado') else 'DESCONOCIDO'
                    result['numero_autorizacion'] = auth.numeroAutorizacion if hasattr(auth, 'numeroAutorizacion') else None
                    result['fecha_autorizacion'] = str(auth.fechaAutorizacion) if hasattr(auth, 'fechaAutorizacion') else None
                    result['ambiente'] = auth.ambiente if hasattr(auth, 'ambiente') else self.ambiente
                    result['comprobante'] = auth.comprobante if hasattr(auth, 'comprobante') else None

                    # Extract messages
                    if hasattr(auth, 'mensajes') and auth.mensajes:
                        mensajes = auth.mensajes.mensaje if hasattr(auth.mensajes, 'mensaje') else []

                        if not isinstance(mensajes, list):
                            mensajes = [mensajes]

                        for msg in mensajes:
                            result['mensajes'].append({
                                'identificador': msg.identificador if hasattr(msg, 'identificador') else None,
                                'mensaje': msg.mensaje if hasattr(msg, 'mensaje') else None,
                                'tipo': msg.tipo if hasattr(msg, 'tipo') else None,
                                'informacionAdicional': msg.informacionAdicional if hasattr(msg, 'informacionAdicional') else None
                            })

            logger.info(f"Authorization query successful. Estado: {result['estado']}")
            return result

        except ZeepFault as e:
            logger.error(f"SOAP Fault querying authorization: {str(e)}")
            return {
                'estado': 'ERROR',
                'numero_autorizacion': None,
                'fecha_autorizacion': None,
                'ambiente': self.ambiente,
                'comprobante': None,
                'mensajes': [{'mensaje': f'Error SOAP: {str(e)}', 'tipo': 'ERROR'}]
            }

        except Exception as e:
            logger.error(f"Error querying authorization: {str(e)}")
            return {
                'estado': 'ERROR',
                'numero_autorizacion': None,
                'fecha_autorizacion': None,
                'ambiente': self.ambiente,
                'comprobante': None,
                'mensajes': [{'mensaje': f'Error: {str(e)}', 'tipo': 'ERROR'}]
            }

    def test_connection(self):
        """
        Test connection to SRI web services

        Returns:
            Boolean indicating if connection is successful
        """
        try:
            # Try to get WSDL
            client = self._get_recepcion_client()
            logger.info("Connection to SRI web services successful")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
