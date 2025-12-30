"""
Routes for Inventario Service
"""
from flask import Blueprint, request
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.auth_middleware import token_required
from common.utils import success_response, error_response, get_pagination_params
from models import ProductModel, TreatmentModel, TreatmentRecipeModel

inventario_bp = Blueprint('inventario', __name__)


# ============= PRODUCTS ENDPOINTS =============

@inventario_bp.route('/products', methods=['GET'])
@token_required
def list_products(current_user):
    """List all products"""
    try:
        # Get query parameters
        pagination = get_pagination_params(request)
        search = request.args.get('search')
        low_stock_only = request.args.get('low_stock', 'false').lower() == 'true'

        # Get products
        products = ProductModel.list_products(
            limit=pagination['per_page'],
            offset=pagination['offset'],
            search=search,
            low_stock_only=low_stock_only
        )

        total = ProductModel.count_products(search=search, low_stock_only=low_stock_only)

        response_data = {
            'products': products,
            'pagination': {
                'page': pagination['page'],
                'per_page': pagination['per_page'],
                'total': total,
                'pages': (total + pagination['per_page'] - 1) // pagination['per_page']
            }
        }

        return success_response(response_data)

    except Exception as e:
        print(f"List products error: {str(e)}")
        return error_response('An error occurred', 500)


@inventario_bp.route('/products/<int:product_id>', methods=['GET'])
@token_required
def get_product(current_user, product_id):
    """Get product by ID"""
    try:
        product = ProductModel.get_by_id(product_id)

        if not product:
            return error_response('Product not found', 404)

        return success_response({'product': product})

    except Exception as e:
        print(f"Get product error: {str(e)}")
        return error_response('An error occurred', 500)


@inventario_bp.route('/products', methods=['POST'])
@token_required
def create_product(current_user):
    """Create new product"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'cost_price', 'sale_price']
        for field in required_fields:
            if field not in data:
                return error_response(f'{field} is required', 400)

        # Check if SKU exists
        if data.get('sku'):
            existing = ProductModel.get_by_sku(data['sku'])
            if existing:
                return error_response('Product with this SKU already exists', 409)

        # Create product
        product = ProductModel.create(
            sku=data.get('sku'),
            name=data['name'],
            description=data.get('description'),
            cost_price=data['cost_price'],
            sale_price=data['sale_price'],
            stock_quantity=data.get('stock_quantity', 0),
            min_stock_alert=data.get('min_stock_alert', 10)
        )

        return success_response({'product': product}, 'Product created successfully', 201)

    except Exception as e:
        print(f"Create product error: {str(e)}")
        return error_response('An error occurred', 500)


@inventario_bp.route('/products/<int:product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    """Update product"""
    try:
        data = request.get_json()

        if not data:
            return error_response('No data to update', 400)

        # Update product
        product = ProductModel.update(product_id, **data)

        if not product:
            return error_response('Product not found', 404)

        return success_response({'product': product}, 'Product updated successfully')

    except Exception as e:
        print(f"Update product error: {str(e)}")
        return error_response('An error occurred', 500)


@inventario_bp.route('/products/<int:product_id>/stock', methods=['PATCH'])
@token_required
def update_stock(current_user, product_id):
    """Update product stock"""
    try:
        data = request.get_json()

        if 'quantity_change' not in data:
            return error_response('quantity_change is required', 400)

        result = ProductModel.update_stock(product_id, data['quantity_change'])

        if not result:
            return error_response('Product not found', 404)

        return success_response({'product': result}, 'Stock updated successfully')

    except Exception as e:
        print(f"Update stock error: {str(e)}")
        return error_response('An error occurred', 500)


@inventario_bp.route('/products/low-stock', methods=['GET'])
@token_required
def get_low_stock(current_user):
    """Get products with low stock"""
    try:
        products = ProductModel.get_low_stock_products()
        return success_response({'products': products, 'count': len(products)})

    except Exception as e:
        print(f"Get low stock error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= TREATMENTS ENDPOINTS =============

@inventario_bp.route('/treatments', methods=['GET'])
@token_required
def list_treatments(current_user):
    """List all treatments"""
    try:
        # Get query parameters
        pagination = get_pagination_params(request)
        search = request.args.get('search')
        category = request.args.get('category')

        # Get treatments
        treatments = TreatmentModel.list_treatments(
            limit=pagination['per_page'],
            offset=pagination['offset'],
            search=search,
            category=category
        )

        total = TreatmentModel.count_treatments(search=search, category=category)

        response_data = {
            'treatments': treatments,
            'pagination': {
                'page': pagination['page'],
                'per_page': pagination['per_page'],
                'total': total,
                'pages': (total + pagination['per_page'] - 1) // pagination['per_page']
            }
        }

        return success_response(response_data)

    except Exception as e:
        print(f"List treatments error: {str(e)}")
        return error_response('An error occurred', 500)


@inventario_bp.route('/treatments/<int:treatment_id>', methods=['GET'])
@token_required
def get_treatment(current_user, treatment_id):
    """Get treatment by ID"""
    try:
        treatment = TreatmentModel.get_by_id(treatment_id)

        if not treatment:
            return error_response('Treatment not found', 404)

        # Get recipe/ingredients
        recipe = TreatmentRecipeModel.get_recipe(treatment_id)
        treatment_cost = TreatmentRecipeModel.calculate_treatment_cost(treatment_id)

        treatment['recipe'] = recipe
        treatment['cost'] = treatment_cost
        treatment['margin'] = float(treatment['base_price']) - treatment_cost

        return success_response({'treatment': treatment})

    except Exception as e:
        print(f"Get treatment error: {str(e)}")
        return error_response('An error occurred', 500)


@inventario_bp.route('/treatments', methods=['POST'])
@token_required
def create_treatment(current_user):
    """Create new treatment"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'base_price']
        for field in required_fields:
            if field not in data:
                return error_response(f'{field} is required', 400)

        # Create treatment
        treatment = TreatmentModel.create(
            name=data['name'],
            category=data.get('category'),
            base_price=data['base_price'],
            description=data.get('description')
        )

        return success_response({'treatment': treatment}, 'Treatment created successfully', 201)

    except Exception as e:
        print(f"Create treatment error: {str(e)}")
        return error_response('An error occurred', 500)


@inventario_bp.route('/treatments/<int:treatment_id>', methods=['PUT'])
@token_required
def update_treatment(current_user, treatment_id):
    """Update treatment"""
    try:
        data = request.get_json()

        if not data:
            return error_response('No data to update', 400)

        # Update treatment
        treatment = TreatmentModel.update(treatment_id, **data)

        if not treatment:
            return error_response('Treatment not found', 404)

        return success_response({'treatment': treatment}, 'Treatment updated successfully')

    except Exception as e:
        print(f"Update treatment error: {str(e)}")
        return error_response('An error occurred', 500)


@inventario_bp.route('/treatments/categories', methods=['GET'])
@token_required
def get_categories(current_user):
    """Get all treatment categories"""
    try:
        categories = TreatmentModel.get_categories()
        return success_response({'categories': categories})

    except Exception as e:
        print(f"Get categories error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= TREATMENT RECIPES ENDPOINTS (Motor de Recetas) =============

@inventario_bp.route('/treatments/<int:treatment_id>/recipe', methods=['GET'])
@token_required
def get_recipe(current_user, treatment_id):
    """Get treatment recipe"""
    try:
        recipe = TreatmentRecipeModel.get_recipe(treatment_id)
        cost = TreatmentRecipeModel.calculate_treatment_cost(treatment_id)

        return success_response({'recipe': recipe, 'total_cost': cost})

    except Exception as e:
        print(f"Get recipe error: {str(e)}")
        return error_response('An error occurred', 500)


@inventario_bp.route('/treatments/<int:treatment_id>/recipe', methods=['POST'])
@token_required
def add_ingredient(current_user, treatment_id):
    """Add ingredient to treatment recipe"""
    try:
        data = request.get_json()

        if 'product_id' not in data or 'quantity_needed' not in data:
            return error_response('product_id and quantity_needed are required', 400)

        ingredient = TreatmentRecipeModel.add_ingredient(
            treatment_id,
            data['product_id'],
            data['quantity_needed']
        )

        return success_response({'ingredient': ingredient}, 'Ingredient added successfully', 201)

    except Exception as e:
        print(f"Add ingredient error: {str(e)}")
        return error_response('An error occurred', 500)


@inventario_bp.route('/treatments/<int:treatment_id>/recipe/<int:product_id>', methods=['DELETE'])
@token_required
def remove_ingredient(current_user, treatment_id, product_id):
    """Remove ingredient from treatment recipe"""
    try:
        result = TreatmentRecipeModel.remove_ingredient(treatment_id, product_id)

        if not result:
            return error_response('Ingredient not found', 404)

        return success_response(message='Ingredient removed successfully')

    except Exception as e:
        print(f"Remove ingredient error: {str(e)}")
        return error_response('An error occurred', 500)


@inventario_bp.route('/treatments/<int:treatment_id>/check-stock', methods=['GET'])
@token_required
def check_stock(current_user, treatment_id):
    """Check stock availability for treatment"""
    try:
        quantity = request.args.get('quantity', 1, type=int)
        availability = TreatmentRecipeModel.check_stock_availability(treatment_id, quantity)

        all_available = all(item['is_available'] for item in availability)

        response_data = {
            'treatment_id': treatment_id,
            'quantity': quantity,
            'all_available': all_available,
            'items': availability
        }

        return success_response(response_data)

    except Exception as e:
        print(f"Check stock error: {str(e)}")
        return error_response('An error occurred', 500)


# Health check
@inventario_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return success_response({'status': 'healthy', 'service': 'inventario'})
