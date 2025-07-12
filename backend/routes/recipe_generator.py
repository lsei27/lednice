from flask import Blueprint, request, jsonify
from ..services.recipe_generator import OpenAIService
from ..services.recipe_database import RecipeDatabase

recipe_bp = Blueprint('recipes', __name__)

@recipe_bp.route('/generate', methods=['POST'])
def generate_recipes():
    try:
        data = request.get_json()
        
        if not data or 'ingredients' not in data:
            return jsonify({'error': 'Chybí seznam ingrediencí'}), 400
        
        ingredients = data['ingredients']
        max_time = data.get('max_time', 20)
        dietary_restrictions = data.get('dietary_restrictions', [])
        
        generator = OpenAIService()
        recipes = generator.generate_recipes(
            ingredients=ingredients,
            max_time=max_time,
            dietary_restrictions=dietary_restrictions
        )
        
        return jsonify({
            'recipes': recipes,
            'total_count': len(recipes),
            'generation_time': 'okamžité'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Chyba při generování receptů: {str(e)}'}), 500

@recipe_bp.route('/search', methods=['GET'])
def search_recipes():
    try:
        ingredients = request.args.get('ingredients', '').split(',')
        max_time = int(request.args.get('max_time', 20))
        
        if not ingredients or ingredients[0] == '':
            return jsonify({'error': 'Nebyly zadány ingredience'}), 400
        
        ingredients = [ing.strip() for ing in ingredients if ing.strip()]
        
        db = RecipeDatabase()
        recipes = db.search_recipes_by_ingredients(ingredients, max_time)
        
        return jsonify({
            'recipes': recipes,
            'search_ingredients': ingredients,
            'max_time': max_time
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Chyba při vyhledávání: {str(e)}'}), 500

@recipe_bp.route('/categories', methods=['GET'])
def get_recipe_categories():
    try:
        db = RecipeDatabase()
        categories = db.get_recipe_categories()
        
        return jsonify({
            'categories': categories
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Chyba při načítání kategorií: {str(e)}'}), 500

@recipe_bp.route('/<recipe_id>', methods=['GET'])
def get_recipe_details(recipe_id):
    try:
        db = RecipeDatabase()
        recipe = db.get_recipe_by_id(recipe_id)
        
        if not recipe:
            return jsonify({'error': 'Recept nebyl nalezen'}), 404
        
        return jsonify({
            'recipe': recipe
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Chyba při načítání receptu: {str(e)}'}), 500 