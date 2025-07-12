import os
import base64
import json
import requests
import traceback
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv('config.env')

class OpenAIService:
    """
    Služba pro komunikaci s OpenAI API pro analýzu obrázků ledničky a generování receptů.
    """
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1"
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY není nastaven v .env souboru")

    def analyze_fridge_image(self, image_path: str) -> List[Dict[str, Any]]:
        try:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            prompt = """
            Analyzuj obsah ledničky na fotografii a identifikuj všechny dostupné ingredience.
            
            Pro každou ingredienci uveď:
            - Název ingredience
            - Kategorii (zelenina, ovoce, maso, mléčné, vejce, těstoviny, rýže, luštěniny, koření, ostatní)
            - Odhadované množství
            - Čerstvost (čerstvé, dobré, spotřebuj brzy)
            
            Vrať výsledek jako JSON objekt s klíčem "ingredients", který obsahuje pole objektů s klíči: name, category, quantity, freshness.
            Vrať pouze validní JSON bez jakéhokoliv dalšího textu, komentářů nebo vysvětlení.
            """
            
            response_str = self._call_vision_api(encoded_image, prompt)
            return self._parse_ingredients_response(response_str)
            
        except Exception as e:
            print(f"Chyba při analýze obrázku: {e}")
            traceback.print_exc()
            return []

    def generate_recipes(self, ingredients: List[Any], 
                         max_time: int = 20, 
                         dietary_restrictions: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generuje recepty na základě seznamu názvů ingrediencí.
        """
        try:
            ingredient_names = []
            for ing in ingredients:
                if isinstance(ing, dict):
                    name = ing.get('name')
                    if name:
                        ingredient_names.append(name)
                elif isinstance(ing, str):
                    ingredient_names.append(ing)

            if not ingredient_names:
                print("Seznam ingrediencí pro generování je prázdný.")
                return []

            ingredients_text = ", ".join(ingredient_names)
            
            prompt = self._create_recipe_prompt(ingredients_text, max_time, dietary_restrictions)
            response_str = self._call_gpt_api(prompt)
            
            return self._parse_recipes_response(response_str)
            
        except Exception as e:
            print(f"Chyba při generování receptů: {e}")
            traceback.print_exc()
            return self._create_fallback_recipes()

    def _call_api(self, data: Dict[str, Any]) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
        
        if response.status_code != 200:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
        
        try:
            content = response.json()['choices'][0]['message']['content']
        except (KeyError, IndexError):
            return ""

        return content if content is not None else ""

    def _call_vision_api(self, encoded_image: str, prompt: str) -> str:
        data = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}]}],
            "max_tokens": 1000,
            "response_format": {"type": "json_object"}
        }
        return self._call_api(data)

    def _call_gpt_api(self, prompt: str) -> str:
        data = {
            "model": "gpt-4o",
            "messages": [{"role": "system", "content": "Jsi expertní kuchař specializující se na rychlé a zdravé recepty."}, {"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }
        return self._call_api(data)

    def _create_recipe_prompt(self, ingredients_text: str, max_time: int, dietary_restrictions: List[str]) -> str:
        restrictions_text = f"\nDietní omezení: {', '.join(dietary_restrictions)}" if dietary_restrictions else ""
        
        return f"""
        Vytvoř 3-5 rychlých a zdravých receptů z těchto ingrediencí: {ingredients_text}.
        Doma jsou běžné suroviny (sůl, pepř, olej, cibule, česnek, mouka, rýže, těstoviny).
        Požadavky: maximální příprava {max_time} minut, zdravé vaření (ne smažení), respektuj spotřebiče (sporák, trouba, gril, mixér).
        {restrictions_text}
        Vrať JSON objekt s klíčem "recipes", což je pole objektů. Každý objekt musí mít klíče: name, prep_time, servings, ingredients (pole stringů), instructions (pole stringů), nutrition_info (objekt), cooking_tips (pole stringů).
        Vrať POUZE validní JSON.
        """

    def _parse_json_response(self, response_str: str) -> Any:
        if not response_str:
            return None
        cleaned_response = response_str.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:-3].strip()
        if not cleaned_response:
            return None
        return json.loads(cleaned_response)

    def _parse_ingredients_response(self, response_str: str) -> List[Dict[str, Any]]:
        try:
            parsed_json = self._parse_json_response(response_str)
            if not parsed_json:
                return []
            
            valid_ingredients = []
            for ingredient in parsed_json.get('ingredients', []):
                if isinstance(ingredient, dict) and 'name' in ingredient:
                    valid_ingredients.append({
                        'name': ingredient.get('name', 'Neznámá ingredience'),
                        'category': ingredient.get('category', 'ostatní'),
                        'quantity': ingredient.get('quantity', 'dostupné'),
                        'freshness': ingredient.get('freshness', 'čerstvé')
                    })
            return valid_ingredients
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Chyba při parsování ingrediencí: {e}")
            return self._fallback_ingredients_parsing(response_str)

    def _parse_recipes_response(self, response_str: str) -> List[Dict[str, Any]]:
        try:
            parsed_json = self._parse_json_response(response_str)
            if not parsed_json:
                return self._create_fallback_recipes()
            
            valid_recipes = []
            for recipe in parsed_json.get('recipes', []):
                if not isinstance(recipe, dict):
                    continue

                new_recipe = {
                    'name': recipe.get('name', 'Recept bez názvu'),
                    'prep_time': int(recipe.get('prep_time', 0)),
                    'servings': int(recipe.get('servings', 1)),
                    'ingredients': recipe.get('ingredients', []),
                    'instructions': recipe.get('instructions', []),
                    'nutrition_info': recipe.get('nutrition_info', {}),
                    'cooking_tips': recipe.get('cooking_tips', [])
                }
                
                new_recipe['tags'] = self._generate_recipe_tags(new_recipe)
                new_recipe['appliances'] = self._detect_appliances(new_recipe)
                
                valid_recipes.append(new_recipe)
            return valid_recipes
        except (json.JSONDecodeError, AttributeError, KeyError, ValueError) as e:
            print(f"Chyba při parsování receptů: {e}")
            traceback.print_exc()
            return self._create_fallback_recipes()

    def _fallback_ingredients_parsing(self, response_str: str) -> List[Dict[str, Any]]:
        print("Používám záložní parsování ingrediencí.")
        return []

    def _generate_recipe_tags(self, recipe: Dict) -> List[str]:
        tags = []
        if recipe.get('prep_time', 99) <= 20:
            tags.append('rychlé')
        
        ingredients_str = ' '.join(str(i) for i in recipe.get('ingredients', [])).lower()
        if 'kuřecí' in ingredients_str or 'kuře' in ingredients_str:
            tags.append('kuřecí')
        if 'ryba' in ingredients_str or 'losos' in ingredients_str or 'tuňák' in ingredients_str:
            tags.append('rybí')
        if any(veg in ingredients_str for veg in ['zelenina', 'mrkev', 'cibule', 'špenát', 'brokolice']):
             tags.append('zeleninové')
        if not any(maso in ingredients_str for maso in ['kuřecí', 'ryba', 'vepřové', 'hovězí']):
            tags.append('vegetariánské')
        tags.append('zdravé')
        return list(set(tags))

    def _detect_appliances(self, recipe: Dict) -> List[str]:
        appliances = ['elektrický sporák']
        instructions = ' '.join(recipe.get('instructions', [])).lower()
        if any(word in instructions for word in ['trouba', 'pečeme', 'pečení']):
            appliances.append('trouba')
        if any(word in instructions for word in ['mikrovln', 'mikrovlnná']):
            appliances.append('mikrovlnná trouba')
        if any(word in instructions for word in ['mixér', 'mixujeme']):
            appliances.append('mixér')
        if any(word in instructions for word in ['gril', 'grilování']):
            appliances.append('elektrický kontaktní gril')
        return list(set(appliances))

    def _create_fallback_recipes(self) -> List[Dict[str, Any]]:
        print("Vracím záložní recepty.")
        return [{'name': 'Záložní recept: Zeleninová polévka', 'prep_time': 15, 'servings': 2, 'ingredients': ['Zelenina z ledničky'], 'instructions': ['Nakrájejte zeleninu.', 'Vařte 15 minut.', 'Ochuťte.'], 'nutrition_info': {}, 'cooking_tips': [], 'tags': ['rychlé', 'zdravé'], 'appliances': ['elektrický sporák']}] 
