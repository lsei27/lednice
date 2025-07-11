from typing import List, Dict, Any
import json
import os

class RecipeDatabase:
    def __init__(self):
        self.recipes = self._load_recipes()
    
    def _load_recipes(self) -> List[Dict[str, Any]]:
        recipes = [
            {
                'id': '1',
                'name': 'Kuřecí prsa s dušenou zeleninou',
                'prep_time': 15,
                'servings': 2,
                'difficulty': 'snadné',
                'tags': ['maso', 'zelenina', 'zdravé', 'rychlé'],
                'ingredients': [
                    {'name': 'kuřecí prsa', 'amount': '200g', 'unit': 'g'},
                    {'name': 'mrkev', 'amount': '2', 'unit': 'ks'},
                    {'name': 'cibule', 'amount': '1', 'unit': 'ks'},
                    {'name': 'paprika', 'amount': '1', 'unit': 'ks'},
                    {'name': 'česnek', 'amount': '2', 'unit': 'stroužky'},
                    {'name': 'olivový olej', 'amount': '1', 'unit': 'lžíce'},
                    {'name': 'sůl', 'amount': '1', 'unit': 'špetka'},
                    {'name': 'pepř', 'amount': '1', 'unit': 'špetka'}
                ],
                'instructions': [
                    'Kuřecí prsa nakrájejte na kousky',
                    'Zeleninu nakrájejte na kousky',
                    'Na pánvi rozehřejte olej',
                    'Opečte kuřecí maso 5 minut',
                    'Přidejte zeleninu a duste 8 minut',
                    'Okořeňte solí a pepřem'
                ],
                'appliances': ['elektrický sporák'],
                'calories': 280,
                'protein': '35g',
                'carbs': '15g',
                'fat': '8g',
                'fiber': '6g',
                'health_rating': 'výborné'
            },
            {
                'id': '2',
                'name': 'Salát s tuňákem a avokádem',
                'prep_time': 10,
                'servings': 2,
                'difficulty': 'snadné',
                'tags': ['ryby', 'zelenina', 'zdravé', 'rychlé'],
                'ingredients': [
                    {'name': 'salát', 'amount': '1', 'unit': 'hlávka'},
                    {'name': 'rajčata', 'amount': '2', 'unit': 'ks'},
                    {'name': 'okurka', 'amount': '1', 'unit': 'ks'},
                    {'name': 'tuňák', 'amount': '1', 'unit': 'konzerva'},
                    {'name': 'avokádový olej', 'amount': '1', 'unit': 'lžíce'},
                    {'name': 'citron', 'amount': '1/2', 'unit': 'ks'},
                    {'name': 'sůl', 'amount': '1', 'unit': 'špetka'}
                ],
                'instructions': [
                    'Salát nakrájejte na kousky',
                    'Rajčata a okurku nakrájejte',
                    'Smíchejte zeleninu v míse',
                    'Přidejte tuňáka',
                    'Zakápněte olejem a citronem',
                    'Okořeňte solí'
                ],
                'appliances': [],
                'calories': 220,
                'protein': '25g',
                'carbs': '8g',
                'fat': '12g',
                'fiber': '4g',
                'health_rating': 'výborné'
            },
            {
                'id': '3',
                'name': 'Omeleta se špenátem a sýrem',
                'prep_time': 12,
                'servings': 1,
                'difficulty': 'snadné',
                'tags': ['vejce', 'zelenina', 'mléčné', 'zdravé'],
                'ingredients': [
                    {'name': 'vajíčka', 'amount': '3', 'unit': 'ks'},
                    {'name': 'špenát', 'amount': '50g', 'unit': 'g'},
                    {'name': 'sýr', 'amount': '30g', 'unit': 'g'},
                    {'name': 'mléko', 'amount': '2', 'unit': 'lžíce'},
                    {'name': 'sůl', 'amount': '1', 'unit': 'špetka'},
                    {'name': 'pepř', 'amount': '1', 'unit': 'špetka'}
                ],
                'instructions': [
                    'Vajíčka rozklepněte do mísy',
                    'Přidejte mléko a rozšlehejte',
                    'Na pánvi opečte špenát',
                    'Přilijte vajíčka',
                    'Posypte sýrem',
                    'Složte a nechte dopéct'
                ],
                'appliances': ['elektrický sporák'],
                'calories': 320,
                'protein': '28g',
                'carbs': '4g',
                'fat': '22g',
                'fiber': '2g',
                'health_rating': 'výborné'
            },
            {
                'id': '4',
                'name': 'Rychlá zeleninová polévka',
                'prep_time': 18,
                'servings': 4,
                'difficulty': 'snadné',
                'tags': ['zelenina', 'vegetariánské', 'zdravé'],
                'ingredients': [
                    {'name': 'cibule', 'amount': '1', 'unit': 'ks'},
                    {'name': 'mrkev', 'amount': '3', 'unit': 'ks'},
                    {'name': 'celer', 'amount': '1', 'unit': 'ks'},
                    {'name': 'brambory', 'amount': '2', 'unit': 'ks'},
                    {'name': 'česnek', 'amount': '2', 'unit': 'stroužky'},
                    {'name': 'zeleninový vývar', 'amount': '1', 'unit': 'litr'},
                    {'name': 'sůl', 'amount': '1', 'unit': 'špetka'},
                    {'name': 'pepř', 'amount': '1', 'unit': 'špetka'}
                ],
                'instructions': [
                    'Cibuli nakrájejte na kostičky',
                    'Zeleninu nakrájejte na kousky',
                    'Na pánvi opečte cibuli',
                    'Přidejte zeleninu a duste 5 minut',
                    'Přilijte vývar a vařte 10 minut',
                    'Okořeňte solí a pepřem'
                ],
                'appliances': ['elektrický sporák'],
                'calories': 120,
                'protein': '4g',
                'carbs': '22g',
                'fat': '2g',
                'fiber': '6g',
                'health_rating': 'výborné'
            },
            {
                'id': '5',
                'name': 'Grilovaný losos s citronem',
                'prep_time': 15,
                'servings': 2,
                'difficulty': 'střední',
                'tags': ['ryby', 'zdravé', 'rychlé'],
                'ingredients': [
                    {'name': 'losos', 'amount': '300g', 'unit': 'g'},
                    {'name': 'citron', 'amount': '1', 'unit': 'ks'},
                    {'name': 'olivový olej', 'amount': '1', 'unit': 'lžíce'},
                    {'name': 'česnek', 'amount': '2', 'unit': 'stroužky'},
                    {'name': 'sůl', 'amount': '1', 'unit': 'špetka'},
                    {'name': 'pepř', 'amount': '1', 'unit': 'špetka'}
                ],
                'instructions': [
                    'Lososa opláchněte a osušte',
                    'Potřete olejem a kořením',
                    'Rozpalte gril na střední teplotu',
                    'Grilujte 6-8 minut z každé strany',
                    'Servírujte s citronem'
                ],
                'appliances': ['elektrický kontaktní gril'],
                'calories': 280,
                'protein': '35g',
                'carbs': '2g',
                'fat': '15g',
                'fiber': '0g',
                'health_rating': 'výborné'
            },
            {
                'id': '6',
                'name': 'Quinoa s dušenou zeleninou',
                'prep_time': 20,
                'servings': 2,
                'difficulty': 'snadné',
                'tags': ['vegetariánské', 'zelenina', 'zdravé'],
                'ingredients': [
                    {'name': 'quinoa', 'amount': '100g', 'unit': 'g'},
                    {'name': 'brokolice', 'amount': '1', 'unit': 'ks'},
                    {'name': 'mrkev', 'amount': '2', 'unit': 'ks'},
                    {'name': 'cibule', 'amount': '1', 'unit': 'ks'},
                    {'name': 'olivový olej', 'amount': '1', 'unit': 'lžíce'},
                    {'name': 'sůl', 'amount': '1', 'unit': 'špetka'}
                ],
                'instructions': [
                    'Quinoa se uvaří podle návodu',
                    'Zeleninu nakrájejte na kousky',
                    'Na pánvi opečte cibuli',
                    'Přidejte zeleninu a duste 8 minut',
                    'Smíchejte s quinoou',
                    'Okořeňte solí'
                ],
                'appliances': ['elektrický sporák'],
                'calories': 250,
                'protein': '8g',
                'carbs': '45g',
                'fat': '6g',
                'fiber': '8g',
                'health_rating': 'výborné'
            }
        ]
        
        return recipes
    
    def get_recipes_by_ingredients(self, ingredients: List[str], max_time: int = 20) -> List[Dict]:
        matching_recipes = []
        
        for recipe in self.recipes:
            if recipe['prep_time'] > max_time:
                continue
            
            recipe_ingredients = [ing['name'].lower() for ing in recipe['ingredients']]
            
            for ingredient in ingredients:
                if any(ingredient in recipe_ing for recipe_ing in recipe_ingredients):
                    matching_recipes.append(recipe)
                    break
        
        return matching_recipes
    
    def search_recipes_by_ingredients(self, ingredients: List[str], max_time: int = 20) -> List[Dict]:
        return self.get_recipes_by_ingredients(ingredients, max_time)
    
    def get_recipe_by_id(self, recipe_id: str) -> Dict:
        for recipe in self.recipes:
            if recipe['id'] == recipe_id:
                return recipe
        return None
    
    def get_recipe_categories(self) -> List[str]:
        categories = set()
        for recipe in self.recipes:
            categories.update(recipe.get('tags', []))
        return list(categories) 