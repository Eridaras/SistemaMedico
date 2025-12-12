"""
XML Storage Management for Electronic Invoices
Handles storage, retrieval, and organization of XML files
"""
import os
import sys
from datetime import datetime
from pathlib import Path
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class XMLStorageManager:
    """
    Manages storage of XML files for electronic invoices

    Directory structure:
    storage/
    ├── xml/
    │   ├── 2024/
    │   │   ├── 12/
    │   │   │   ├── facturas/
    │   │   │   │   ├── 001-001-000000001.xml
    │   │   │   │   ├── 001-001-000000002.xml
    │   │   │   ├── autorizados/
    │   │   │   │   ├── 001-001-000000001_AUTORIZADO.xml
    │   │   │   ├── rechazados/
    │   │   │       ├── 001-001-000000003_ERROR.xml
    │   ├── ride/
    │   │   ├── 2024/
    │   │   │   ├── 12/
    │   │   │   │   ├── 001-001-000000001.pdf
    """

    def __init__(self, base_path=None):
        """
        Initialize XML Storage Manager

        Args:
            base_path: Base directory for storage (default: backend/storage)
        """
        if base_path is None:
            # Default to backend/storage
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            base_path = os.path.join(backend_dir, 'storage')

        self.base_path = Path(base_path)
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directory structure"""
        # Main directories
        self.xml_dir = self.base_path / 'xml'
        self.ride_dir = self.base_path / 'ride'
        self.backup_dir = self.base_path / 'backup'

        # Create if they don't exist
        self.xml_dir.mkdir(parents=True, exist_ok=True)
        self.ride_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _get_date_path(self, base_dir, date=None):
        """
        Get year/month subdirectory path

        Args:
            base_dir: Base directory (xml or ride)
            date: Date object (default: today)

        Returns:
            Path object for year/month directory
        """
        if date is None:
            date = datetime.now()

        year = str(date.year)
        month = f"{date.month:02d}"

        path = base_dir / year / month
        path.mkdir(parents=True, exist_ok=True)

        return path

    def save_xml(self, invoice_number, xml_content, estado='PENDIENTE', date=None):
        """
        Save XML file organized by date and status

        Args:
            invoice_number: Invoice number (e.g., "001-001-000000001")
            xml_content: XML content as string
            estado: Status (PENDIENTE, AUTORIZADO, RECHAZADO)
            date: Date for organization (default: today)

        Returns:
            Full path to saved file
        """
        # Get date-based directory
        date_path = self._get_date_path(self.xml_dir, date)

        # Create status subdirectory
        if estado == 'AUTORIZADO' or estado == 'AUTORIZADA':
            status_dir = date_path / 'autorizados'
        elif estado in ['RECHAZADO', 'NO_AUTORIZADO', 'NO_AUTORIZADA', 'ERROR']:
            status_dir = date_path / 'rechazados'
        else:
            status_dir = date_path / 'facturas'

        status_dir.mkdir(exist_ok=True)

        # Filename
        if estado == 'AUTORIZADO' or estado == 'AUTORIZADA':
            filename = f"{invoice_number}_AUTORIZADO.xml"
        elif estado in ['RECHAZADO', 'NO_AUTORIZADO', 'NO_AUTORIZADA', 'ERROR']:
            filename = f"{invoice_number}_{estado}.xml"
        else:
            filename = f"{invoice_number}.xml"

        filepath = status_dir / filename

        # Save XML
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)

        return str(filepath)

    def get_xml(self, invoice_number, estado='PENDIENTE', date=None):
        """
        Retrieve XML file

        Args:
            invoice_number: Invoice number
            estado: Status to look for
            date: Date of the file (default: today)

        Returns:
            XML content as string or None if not found
        """
        date_path = self._get_date_path(self.xml_dir, date)

        # Determine subdirectory
        if estado == 'AUTORIZADO' or estado == 'AUTORIZADA':
            status_dir = date_path / 'autorizados'
            filename = f"{invoice_number}_AUTORIZADO.xml"
        elif estado in ['RECHAZADO', 'NO_AUTORIZADO', 'NO_AUTORIZADA', 'ERROR']:
            status_dir = date_path / 'rechazados'
            filename = f"{invoice_number}_{estado}.xml"
        else:
            status_dir = date_path / 'facturas'
            filename = f"{invoice_number}.xml"

        filepath = status_dir / filename

        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()

        return None

    def save_ride(self, invoice_number, pdf_content, date=None):
        """
        Save RIDE PDF file

        Args:
            invoice_number: Invoice number
            pdf_content: PDF content as bytes
            date: Date for organization (default: today)

        Returns:
            Full path to saved file
        """
        date_path = self._get_date_path(self.ride_dir, date)
        filename = f"{invoice_number}.pdf"
        filepath = date_path / filename

        # Save PDF
        with open(filepath, 'wb') as f:
            f.write(pdf_content)

        return str(filepath)

    def get_ride(self, invoice_number, date=None):
        """
        Retrieve RIDE PDF file

        Args:
            invoice_number: Invoice number
            date: Date of the file (default: today)

        Returns:
            PDF content as bytes or None if not found
        """
        date_path = self._get_date_path(self.ride_dir, date)
        filename = f"{invoice_number}.pdf"
        filepath = date_path / filename

        if filepath.exists():
            with open(filepath, 'rb') as f:
                return f.read()

        return None

    def backup_xml(self, invoice_number, xml_content):
        """
        Create backup of XML with timestamp

        Args:
            invoice_number: Invoice number
            xml_content: XML content

        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{invoice_number}_{timestamp}.xml"
        filepath = self.backup_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)

        return str(filepath)

    def list_xmls(self, year=None, month=None, estado=None):
        """
        List XML files with optional filters

        Args:
            year: Filter by year
            month: Filter by month
            estado: Filter by status

        Returns:
            List of file paths
        """
        files = []

        if year and month:
            # Specific year/month
            date_path = self.xml_dir / str(year) / f"{month:02d}"
            if date_path.exists():
                if estado:
                    if estado == 'AUTORIZADO':
                        search_dir = date_path / 'autorizados'
                    elif estado in ['RECHAZADO', 'ERROR']:
                        search_dir = date_path / 'rechazados'
                    else:
                        search_dir = date_path / 'facturas'

                    if search_dir.exists():
                        files = list(search_dir.glob('*.xml'))
                else:
                    # All statuses
                    for subdir in ['facturas', 'autorizados', 'rechazados']:
                        subdir_path = date_path / subdir
                        if subdir_path.exists():
                            files.extend(list(subdir_path.glob('*.xml')))
        else:
            # All files
            files = list(self.xml_dir.rglob('*.xml'))

        return [str(f) for f in files]

    def calculate_checksum(self, xml_content):
        """
        Calculate SHA256 checksum of XML content

        Args:
            xml_content: XML content as string

        Returns:
            SHA256 hash as hex string
        """
        return hashlib.sha256(xml_content.encode('utf-8')).hexdigest()

    def verify_xml(self, invoice_number, xml_content, date=None):
        """
        Verify if stored XML matches provided content

        Args:
            invoice_number: Invoice number
            xml_content: XML content to verify
            date: Date of stored file

        Returns:
            Boolean indicating if checksums match
        """
        stored_xml = self.get_xml(invoice_number, date=date)

        if stored_xml is None:
            return False

        stored_checksum = self.calculate_checksum(stored_xml)
        provided_checksum = self.calculate_checksum(xml_content)

        return stored_checksum == provided_checksum

    def get_storage_stats(self):
        """
        Get storage statistics

        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_xmls': len(list(self.xml_dir.rglob('*.xml'))),
            'total_rides': len(list(self.ride_dir.rglob('*.pdf'))),
            'total_backups': len(list(self.backup_dir.glob('*.xml'))),
            'size_mb': 0
        }

        # Calculate total size
        total_size = 0
        for directory in [self.xml_dir, self.ride_dir, self.backup_dir]:
            for file in directory.rglob('*'):
                if file.is_file():
                    total_size += file.stat().st_size

        stats['size_mb'] = round(total_size / (1024 * 1024), 2)

        return stats


# Singleton instance
xml_storage = XMLStorageManager()
