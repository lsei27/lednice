from typing import List, Dict, Any
import random
from .openai_service import OpenAIService
import json

class RecipeGenerator:
    def __init__(self):
        self.available_appliances = [
            'elektrický sporák', 'trouba', 'mikrovlnná trouba', 
            'horkovzdušná parní fritéza', 'mixér', 'tyčový mixér',
            'elektrický kontaktní gril', 'toastovač'
        ]
        
        try:
            self.openai_service = OpenAIService()
            self.use_openai = True
        except Exception as e:
            print(f"OpenAI služba není dostupná: {e}")
            self.use_openai = False
    
    def generate_recipes(self, ingredients: List[Dict[str, Any]], 
                        max_time: int = 20, 
                        dietary_restrictions: List[str] = None) -> List[Dict[str, Any]]:
        if not self.use_openai:
            raise RuntimeError("OpenAI API není dostupné. Nastavte správně OPENAI_API_KEY.")
        try:
            print("🤖 Používám OpenAI GPT pro generování receptů...")
            ai_recipes = self.openai_service.generate_recipes(
                ingredients, max_time, dietary_restrictions
            )
            if ai_recipes:
                enriched_recipes = self._enrich_recipes(ai_recipes, ingredients)
                return enriched_recipes
            else:
                return []
        except Exception as e:
            print(f"Chyba při generování receptů: {e}")
            return []
    
    def _filter_by_dietary_restrictions(self, recipes: List[Dict], 
                                      restrictions: List[str]) -> List[Dict]:
        filtered_recipes = []
        
        for recipe in recipes:
            if self._recipe_matches_dietary_restrictions(recipe, restrictions):
                filtered_recipes.append(recipe)
        
        return filtered_recipes
    
    def _recipe_matches_dietary_restrictions(self, recipe: Dict, 
                                           restrictions: List[str]) -> bool:
        recipe_tags = recipe.get('tags', [])
        
        for restriction in restrictions:
            restriction_lower = restriction.lower()
            
            if 'vegetariánské' in restriction_lower and 'maso' in recipe_tags:
                return False
            
            if 'veganské' in restriction_lower and ('maso' in recipe_tags or 'mléčné' in recipe_tags):
                return False
            
            if 'bezlepkové' in restriction_lower and 'lepek' in recipe_tags:
                return False
        
        return True
    
    def _select_best_recipes(self, recipes: List[Dict], 
                           available_ingredients: List[str]) -> List[Dict]:
        scored_recipes = []
        
        for recipe in recipes:
            score = self._calculate_recipe_score(recipe, available_ingredients)
            scored_recipes.append((recipe, score))
        
        scored_recipes.sort(key=lambda x: x[1], reverse=True)
        selected_recipes = [recipe for recipe, score in scored_recipes[:5]]
        
        return selected_recipes
    
    def _calculate_recipe_score(self, recipe: Dict, 
                              available_ingredients: List[str]) -> float:
        recipe_ingredients = recipe.get('ingredients', [])
        available_set = set(available_ingredients)
        
        available_count = 0
        for ingredient in recipe_ingredients:
            if ingredient['name'].lower() in available_set:
                available_count += 1
        
        if len(recipe_ingredients) > 0:
            availability_ratio = available_count / len(recipe_ingredients)
        else:
            availability_ratio = 0
        
        time_bonus = max(0, (20 - recipe.get('prep_time', 20)) / 20)
        total_score = availability_ratio * 0.7 + time_bonus * 0.3
        
        return total_score
    
    def _enrich_recipes(self, recipes: List[Dict], 
                       available_ingredients: List[Dict]) -> List[Dict]:
        enriched_recipes = []
        
        for recipe in recipes:
            enriched_recipe = recipe.copy()
            
            # Přidání informací o dostupnosti ingrediencí
            enriched_recipe['ingredient_availability'] = self._get_ingredient_availability(
                recipe, available_ingredients
            )
            
            # Přidání tipů pro vaření
            if 'cooking_tips' not in enriched_recipe:
                enriched_recipe['cooking_tips'] = self._generate_cooking_tips(recipe)
            
            # Přidání nutričních informací
            if 'nutrition_info' not in enriched_recipe:
                enriched_recipe['nutrition_info'] = self._get_nutrition_info(recipe)
            
            enriched_recipes.append(enriched_recipe)
        
        return enriched_recipes
    
    def _get_ingredient_availability(self, recipe: Dict, 
                                   available_ingredients: List[Dict]) -> Dict[str, Any]:
        recipe_ingredients = recipe.get('ingredients', [])
        available_names = [ing['name'].lower() for ing in available_ingredients]
        
        available_count = 0
        missing_ingredients = []
        
        for ingredient in recipe_ingredients:
            ingredient_name = ingredient['name'].lower()
            if ingredient_name in available_names:
                available_count += 1
            else:
                missing_ingredients.append(ingredient['name'])
        
        total_count = len(recipe_ingredients)
        availability_percentage = (available_count / total_count * 100) if total_count > 0 else 0
        
        return {
            'available_count': available_count,
            'total_count': total_count,
            'availability_percentage': round(availability_percentage, 1),
            'missing_ingredients': missing_ingredients
        }
    
    def _generate_cooking_tips(self, recipe: Dict) -> List[str]:
        tips = []
        
        if recipe.get('prep_time', 0) <= 10:
            tips.append("Připravte si všechny ingredience předem pro rychlejší vaření")
        
        if any('zelenina' in ing['name'].lower() for ing in recipe.get('ingredients', [])):
            tips.append("Zeleninu vařte al dente pro zachování vitamínů")
        
        if any('maso' in ing['name'].lower() for ing in recipe.get('ingredients', [])):
            tips.append("Maso nechte odležet před krájením pro lepší chuť")
        
        return tips
    
    def _get_nutrition_info(self, recipe: Dict) -> Dict[str, Any]:
        # Simulace nutričních informací
        base_calories = 200
        base_protein = 15
        base_carbs = 25
        base_fat = 8
        
        # Úprava podle ingrediencí
        ingredients = recipe.get('ingredients', [])
        for ingredient in ingredients:
            if 'maso' in ingredient['name'].lower():
                base_protein += 10
                base_calories += 50
            elif 'zelenina' in ingredient['name'].lower():
                base_calories += 20
                base_carbs += 5
        
        return {
            'calories': base_calories,
            'protein': base_protein,
            'carbs': base_carbs,
            'fat': base_fat
        } 

    def _parse_ingredients_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Očekává plain text odpověď: čárkami oddělený seznam názvů ingrediencí.
        Vrací list dictů: [{"name": ...}]
        """
        cleaned_response = response.strip()
        if not cleaned_response:
            print("Odpověď od OpenAI je prázdná!")
            return []
        try:
            # Rozdělení podle čárek, odstranění whitespace, filtrování prázdných
            names = [name.strip() for name in cleaned_response.split(',') if name.strip()]
            return [{"name": name} for name in names]
        except Exception as e:
            print(f"Chyba při parsování ingrediencí: {e}")
            print(f"Odpověď od OpenAI byla: {response}")
            return self._fallback_ingredients_parsing(response)

    def _fallback_ingredients_parsing(self, response: str) -> List[Dict[str, Any]]:
        print(f"Fallback parsování ingrediencí z plain textu: {response}")
        # Stejná logika jako výše, ale robustněji ignoruje whitespace a prázdné položky
        names = [name.strip() for name in response.split(',') if name.strip()]
        return [{"name": name} for name in names] 
