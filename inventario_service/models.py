"""
Models for Inventario Service
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.database import db


class ProductModel:
    """Product database operations"""

    @staticmethod
    def get_by_id(product_id):
        """Get product by ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT product_id, sku, name, description, cost_price, sale_price,
                       stock_quantity, min_stock_alert, is_active
                FROM products
                WHERE product_id = %s
            """, (product_id,))
            return cursor.fetchone()

    @staticmethod
    def get_by_sku(sku):
        """Get product by SKU"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT product_id, sku, name, description, cost_price, sale_price,
                       stock_quantity, min_stock_alert, is_active
                FROM products
                WHERE sku = %s
            """, (sku,))
            return cursor.fetchone()

    @staticmethod
    def list_products(limit=20, offset=0, search=None, low_stock_only=False):
        """List products with filters"""
        query = """
            SELECT product_id, sku, name, description, cost_price, sale_price,
                   stock_quantity, min_stock_alert, is_active
            FROM products
            WHERE is_active = TRUE
        """
        params = []

        if search:
            query += " AND (name ILIKE %s OR sku ILIKE %s OR description ILIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])

        if low_stock_only:
            query += " AND stock_quantity <= min_stock_alert"

        query += " ORDER BY name LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def count_products(search=None, low_stock_only=False):
        """Count products with filters"""
        query = "SELECT COUNT(*) as count FROM products WHERE is_active = TRUE"
        params = []

        if search:
            query += " AND (name ILIKE %s OR sku ILIKE %s OR description ILIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])

        if low_stock_only:
            query += " AND stock_quantity <= min_stock_alert"

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['count'] if result else 0

    @staticmethod
    def create(sku, name, description, cost_price, sale_price, stock_quantity, min_stock_alert):
        """Create a new product"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO products (sku, name, description, cost_price, sale_price,
                                    stock_quantity, min_stock_alert)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING product_id, sku, name, description, cost_price, sale_price,
                          stock_quantity, min_stock_alert, is_active
            """, (sku, name, description, cost_price, sale_price, stock_quantity, min_stock_alert))
            return cursor.fetchone()

    @staticmethod
    def update(product_id, **kwargs):
        """Update product"""
        allowed_fields = ['sku', 'name', 'description', 'cost_price', 'sale_price',
                         'stock_quantity', 'min_stock_alert', 'is_active']

        updates = []
        params = []

        for field in allowed_fields:
            if field in kwargs and kwargs[field] is not None:
                updates.append(f"{field} = %s")
                params.append(kwargs[field])

        if not updates:
            return None

        params.append(product_id)
        query = f"""
            UPDATE products
            SET {', '.join(updates)}
            WHERE product_id = %s
            RETURNING product_id, sku, name, description, cost_price, sale_price,
                      stock_quantity, min_stock_alert, is_active
        """

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    @staticmethod
    def update_stock(product_id, quantity_change):
        """Update product stock quantity"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE products
                SET stock_quantity = stock_quantity + %s
                WHERE product_id = %s
                RETURNING product_id, stock_quantity
            """, (quantity_change, product_id))
            return cursor.fetchone()

    @staticmethod
    def get_low_stock_products():
        """Get products with low stock"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT product_id, sku, name, stock_quantity, min_stock_alert
                FROM products
                WHERE is_active = TRUE AND stock_quantity <= min_stock_alert
                ORDER BY stock_quantity ASC
            """)
            return cursor.fetchall()


class TreatmentModel:
    """Treatment database operations"""

    @staticmethod
    def get_by_id(treatment_id):
        """Get treatment by ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT treatment_id, name, category, base_price, description, is_active
                FROM treatments
                WHERE treatment_id = %s
            """, (treatment_id,))
            return cursor.fetchone()

    @staticmethod
    def list_treatments(limit=20, offset=0, search=None, category=None):
        """List treatments with filters"""
        query = """
            SELECT treatment_id, name, category, base_price, description, is_active
            FROM treatments
            WHERE is_active = TRUE
        """
        params = []

        if search:
            query += " AND (name ILIKE %s OR description ILIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])

        if category:
            query += " AND category = %s"
            params.append(category)

        query += " ORDER BY name LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def count_treatments(search=None, category=None):
        """Count treatments"""
        query = "SELECT COUNT(*) as count FROM treatments WHERE is_active = TRUE"
        params = []

        if search:
            query += " AND (name ILIKE %s OR description ILIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])

        if category:
            query += " AND category = %s"
            params.append(category)

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['count'] if result else 0

    @staticmethod
    def create(name, category, base_price, description):
        """Create a new treatment"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO treatments (name, category, base_price, description)
                VALUES (%s, %s, %s, %s)
                RETURNING treatment_id, name, category, base_price, description, is_active
            """, (name, category, base_price, description))
            return cursor.fetchone()

    @staticmethod
    def update(treatment_id, **kwargs):
        """Update treatment"""
        allowed_fields = ['name', 'category', 'base_price', 'description', 'is_active']

        updates = []
        params = []

        for field in allowed_fields:
            if field in kwargs and kwargs[field] is not None:
                updates.append(f"{field} = %s")
                params.append(kwargs[field])

        if not updates:
            return None

        params.append(treatment_id)
        query = f"""
            UPDATE treatments
            SET {', '.join(updates)}
            WHERE treatment_id = %s
            RETURNING treatment_id, name, category, base_price, description, is_active
        """

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    @staticmethod
    def get_categories():
        """Get unique treatment categories"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT category
                FROM treatments
                WHERE category IS NOT NULL AND is_active = TRUE
                ORDER BY category
            """)
            return [row['category'] for row in cursor.fetchall()]


class TreatmentRecipeModel:
    """Treatment Recipe database operations (Motor de Recetas)"""

    @staticmethod
    def get_recipe(treatment_id):
        """Get complete recipe for a treatment"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT tr.recipe_id, tr.treatment_id, tr.product_id, tr.quantity_needed,
                       p.name as product_name, p.sku, p.cost_price, p.stock_quantity
                FROM treatment_recipes tr
                JOIN products p ON tr.product_id = p.product_id
                WHERE tr.treatment_id = %s
                ORDER BY p.name
            """, (treatment_id,))
            return cursor.fetchall()

    @staticmethod
    def add_ingredient(treatment_id, product_id, quantity_needed):
        """Add ingredient to treatment recipe"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO treatment_recipes (treatment_id, product_id, quantity_needed)
                VALUES (%s, %s, %s)
                ON CONFLICT (treatment_id, product_id)
                DO UPDATE SET quantity_needed = EXCLUDED.quantity_needed
                RETURNING recipe_id, treatment_id, product_id, quantity_needed
            """, (treatment_id, product_id, quantity_needed))
            return cursor.fetchone()

    @staticmethod
    def remove_ingredient(treatment_id, product_id):
        """Remove ingredient from treatment recipe"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                DELETE FROM treatment_recipes
                WHERE treatment_id = %s AND product_id = %s
                RETURNING recipe_id
            """, (treatment_id, product_id))
            return cursor.fetchone()

    @staticmethod
    def calculate_treatment_cost(treatment_id):
        """Calculate the total cost of ingredients for a treatment"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT SUM(tr.quantity_needed * p.cost_price) as total_cost
                FROM treatment_recipes tr
                JOIN products p ON tr.product_id = p.product_id
                WHERE tr.treatment_id = %s
            """, (treatment_id,))
            result = cursor.fetchone()
            return float(result['total_cost']) if result and result['total_cost'] else 0.0

    @staticmethod
    def check_stock_availability(treatment_id, quantity=1):
        """Check if there's enough stock for the treatment"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT tr.product_id, p.name as product_name,
                       tr.quantity_needed, p.stock_quantity,
                       (tr.quantity_needed * %s) as required_quantity,
                       CASE
                           WHEN p.stock_quantity >= (tr.quantity_needed * %s) THEN TRUE
                           ELSE FALSE
                       END as is_available
                FROM treatment_recipes tr
                JOIN products p ON tr.product_id = p.product_id
                WHERE tr.treatment_id = %s
            """, (quantity, quantity, treatment_id))
            return cursor.fetchall()
