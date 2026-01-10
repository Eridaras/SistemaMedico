"""
Models for Facturacion Service
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.database import db


class InvoiceModel:
    """Invoice database operations"""

    @staticmethod
    def get_by_id(invoice_id):
        """Get invoice by ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT i.invoice_id, i.patient_id,
                       i.invoice_date, i.subtotal, i.iva_percentage, i.iva, i.total, i.status,
                       i.payment_method, i.authorization_number,
                       p.full_name as patient_name,
                       p.identification_type as doc_type, p.identification as doc_number,
                       p.email, p.phone, p.address
                FROM invoices i
                LEFT JOIN patients p ON i.patient_id = p.patient_id
                WHERE i.invoice_id = %s
            """, (invoice_id,))
            return cursor.fetchone()

    @staticmethod
    def list_invoices(limit=20, offset=0, status=None, date_from=None, date_to=None):
        """List invoices with filters"""
        query = """
            SELECT i.invoice_id, i.patient_id,
                   i.invoice_date, i.subtotal, i.iva_percentage, i.iva, i.total, i.status,
                   i.payment_method,
                   p.full_name as patient_name
            FROM invoices i
            LEFT JOIN patients p ON i.patient_id = p.patient_id
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND i.status = %s"
            params.append(status)

        if date_from:
            query += " AND i.invoice_date >= %s"
            params.append(date_from)

        if date_to:
            query += " AND i.invoice_date <= %s"
            params.append(date_to)

        query += " ORDER BY i.invoice_date DESC, i.invoice_id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def count_invoices(status=None, date_from=None, date_to=None):
        """Count invoices"""
        query = "SELECT COUNT(*) as count FROM invoices WHERE 1=1"
        params = []

        if status:
            query += " AND status = %s"
            params.append(status)

        if date_from:
            query += " AND invoice_date >= %s"
            params.append(date_from)

        if date_to:
            query += " AND invoice_date <= %s"
            params.append(date_to)

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['count'] if result else 0

    @staticmethod
    def create(patient_id, appointment_id, invoice_number, issue_date, subtotal, iva_rate, iva_amount, total_amount, status='DRAFT'):
        """Create a new invoice"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO invoices (patient_id, appointment_id, invoice_number, issue_date,
                                    subtotal, iva_rate, iva_amount, total_amount, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING invoice_id, patient_id, appointment_id, invoice_number, issue_date,
                         subtotal, iva_rate, iva_amount, total_amount, status
            """, (patient_id, appointment_id, invoice_number, issue_date, subtotal, iva_rate, iva_amount, total_amount, status))
            return cursor.fetchone()

    @staticmethod
    def update(invoice_id, **kwargs):
        """Update invoice"""
        allowed_fields = ['patient_id', 'appointment_id', 'invoice_number', 'issue_date',
                         'subtotal', 'iva_rate', 'iva_amount', 'total_amount', 'status']

        updates = []
        params = []

        for field in allowed_fields:
            if field in kwargs and kwargs[field] is not None:
                updates.append(f"{field} = %s")
                params.append(kwargs[field])

        if not updates:
            return None

        params.append(invoice_id)
        query = f"""
            UPDATE invoices
            SET {', '.join(updates)}
            WHERE invoice_id = %s
            RETURNING invoice_id, patient_id, appointment_id, invoice_number, issue_date,
                     subtotal, iva_rate, iva_amount, total_amount, status
        """

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    @staticmethod
    def update_status(invoice_id, status):
        """Update invoice status"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE invoices
                SET status = %s
                WHERE invoice_id = %s
                RETURNING invoice_id, status
            """, (status, invoice_id))
            return cursor.fetchone()

    @staticmethod
    def get_totals_by_period(date_from=None, date_to=None):
        """Get invoice totals for a period"""
        query = """
            SELECT
                COUNT(*) as invoice_count,
                COALESCE(SUM(subtotal), 0) as total_subtotal,
                COALESCE(SUM(iva_amount), 0) as total_iva,
                COALESCE(SUM(total_amount), 0) as total_amount,
                status
            FROM invoices
            WHERE 1=1
        """
        params = []

        if date_from:
            query += " AND invoice_date >= %s"
            params.append(date_from)

        if date_to:
            query += " AND invoice_date <= %s"
            params.append(date_to)

        query += " GROUP BY status"

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def get_next_invoice_number():
        """Generate next invoice number"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT invoice_number
                FROM invoices
                WHERE invoice_number IS NOT NULL
                ORDER BY invoice_id DESC
                LIMIT 1
            """)
            result = cursor.fetchone()

            if result and result['invoice_number']:
                # Extract number from format like "001-001-000001234"
                parts = result['invoice_number'].split('-')
                if len(parts) == 3:
                    last_number = int(parts[2])
                    return f"{parts[0]}-{parts[1]}-{last_number + 1:09d}"

            # Default starting number
            return "001-001-000000001"


class OperationalExpenseModel:
    """Operational Expense database operations"""

    @staticmethod
    def get_by_id(expense_id):
        """Get expense by ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT oe.expense_id, oe.description, oe.amount, oe.expense_date,
                       oe.category, oe.registered_by,
                       u.full_name as registered_by_name
                FROM operational_expenses oe
                LEFT JOIN users u ON oe.registered_by = u.user_id
                WHERE oe.expense_id = %s
            """, (expense_id,))
            return cursor.fetchone()

    @staticmethod
    def list_expenses(limit=20, offset=0, category=None, date_from=None, date_to=None):
        """List expenses with filters"""
        query = """
            SELECT oe.expense_id, oe.description, oe.amount, oe.expense_date,
                   oe.category, oe.registered_by,
                   u.full_name as registered_by_name
            FROM operational_expenses oe
            LEFT JOIN users u ON oe.registered_by = u.user_id
            WHERE 1=1
        """
        params = []

        if category:
            query += " AND oe.category = %s"
            params.append(category)

        if date_from:
            query += " AND oe.expense_date >= %s"
            params.append(date_from)

        if date_to:
            query += " AND oe.expense_date <= %s"
            params.append(date_to)

        query += " ORDER BY oe.expense_date DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def count_expenses(category=None, date_from=None, date_to=None):
        """Count expenses"""
        query = "SELECT COUNT(*) as count FROM operational_expenses WHERE 1=1"
        params = []

        if category:
            query += " AND category = %s"
            params.append(category)

        if date_from:
            query += " AND expense_date >= %s"
            params.append(date_from)

        if date_to:
            query += " AND expense_date <= %s"
            params.append(date_to)

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['count'] if result else 0

    @staticmethod
    def create(description, amount, expense_date, category, registered_by):
        """Create a new expense"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO operational_expenses (description, amount, expense_date, category, registered_by)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING expense_id, description, amount, expense_date, category, registered_by
            """, (description, amount, expense_date, category, registered_by))
            return cursor.fetchone()

    @staticmethod
    def update(expense_id, **kwargs):
        """Update expense"""
        allowed_fields = ['description', 'amount', 'expense_date', 'category']

        updates = []
        params = []

        for field in allowed_fields:
            if field in kwargs and kwargs[field] is not None:
                updates.append(f"{field} = %s")
                params.append(kwargs[field])

        if not updates:
            return None

        params.append(expense_id)
        query = f"""
            UPDATE operational_expenses
            SET {', '.join(updates)}
            WHERE expense_id = %s
            RETURNING expense_id, description, amount, expense_date, category, registered_by
        """

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    @staticmethod
    def delete(expense_id):
        """Delete expense"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                DELETE FROM operational_expenses
                WHERE expense_id = %s
                RETURNING expense_id
            """, (expense_id,))
            return cursor.fetchone()

    @staticmethod
    def get_totals_by_period(date_from=None, date_to=None):
        """Get expense totals for a period"""
        query = """
            SELECT
                COUNT(*) as expense_count,
                COALESCE(SUM(amount), 0) as total_amount,
                category
            FROM operational_expenses
            WHERE 1=1
        """
        params = []

        if date_from:
            query += " AND expense_date >= %s"
            params.append(date_from)

        if date_to:
            query += " AND expense_date <= %s"
            params.append(date_to)

        query += " GROUP BY category"

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def get_categories():
        """Get unique expense categories"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT category
                FROM operational_expenses
                WHERE category IS NOT NULL
                ORDER BY category
            """)
            return [row['category'] for row in cursor.fetchall()]


class FinancialReportModel:
    """Financial report operations"""

    @staticmethod
    def get_dashboard_metrics(date_from=None, date_to=None):
        """Get financial dashboard metrics"""
        with db.get_cursor() as cursor:
            # Get income (from invoices with status ISSUED or PAID)
            query_income = """
                SELECT
                    COALESCE(SUM(total), 0) as total_income,
                    COUNT(*) as invoice_count
                FROM invoices
                WHERE status IN ('paid', 'pending')
            """
            params_income = []

            if date_from:
                query_income += " AND invoice_date >= %s"
                params_income.append(date_from)

            if date_to:
                query_income += " AND invoice_date <= %s"
                params_income.append(date_to)

            cursor.execute(query_income, params_income)
            income_data = cursor.fetchone()

            # Get expenses
            query_expenses = """
                SELECT
                    COALESCE(SUM(amount), 0) as total_expenses,
                    COUNT(*) as expense_count
                FROM expenses
                WHERE 1=1
            """
            params_expenses = []

            if date_from:
                query_expenses += " AND expense_date >= %s"
                params_expenses.append(date_from)

            if date_to:
                query_expenses += " AND expense_date <= %s"
                params_expenses.append(date_to)

            cursor.execute(query_expenses, params_expenses)
            expense_data = cursor.fetchone()

            # Calculate profit
            total_income = float(income_data['total_income'])
            total_expenses = float(expense_data['total_expenses'])
            profit = total_income - total_expenses

            return {
                'total_income': total_income,
                'invoice_count': income_data['invoice_count'],
                'total_expenses': total_expenses,
                'expense_count': expense_data['expense_count'],
                'profit': profit,
                'profit_margin': (profit / total_income * 100) if total_income > 0 else 0
            }

    @staticmethod
    def get_monthly_summary(date_from, date_to):
        """Get monthly income vs expenses for charts"""
        import calendar
        from datetime import datetime

        with db.get_cursor() as cursor:
            # Get monthly income grouped by month
            cursor.execute("""
                SELECT
                    TO_CHAR(invoice_date, 'Mon') as month_name,
                    EXTRACT(MONTH FROM invoice_date) as month_num,
                    COALESCE(SUM(total), 0) as ingresos
                FROM invoices
                WHERE invoice_date BETWEEN %s AND %s
                    AND status IN ('paid', 'pending')
                GROUP BY month_num, month_name
                ORDER BY month_num
            """, (date_from, date_to))

            income_by_month = {row['month_name']: float(row['ingresos']) for row in cursor.fetchall()}

            # Get monthly expenses grouped by month
            cursor.execute("""
                SELECT
                    TO_CHAR(expense_date, 'Mon') as month_name,
                    EXTRACT(MONTH FROM expense_date) as month_num,
                    COALESCE(SUM(amount), 0) as egresos
                FROM expenses
                WHERE expense_date BETWEEN %s AND %s
                GROUP BY month_num, month_name
                ORDER BY month_num
            """, (date_from, date_to))

            expense_by_month = {row['month_name']: float(row['egresos']) for row in cursor.fetchall()}

            # Combine data for last 6 months
            result = []
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            end_date = datetime.strptime(date_to, '%Y-%m-%d')

            current = start_date
            while current <= end_date:
                month_abbr = current.strftime('%b')
                result.append({
                    'name': month_abbr,
                    'ingresos': income_by_month.get(month_abbr, 0),
                    'egresos': expense_by_month.get(month_abbr, 0)
                })

                # Move to next month
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)

            return result
