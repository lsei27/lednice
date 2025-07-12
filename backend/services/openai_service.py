import os
import base64
import json
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv('config.env')

class OpenAIService:
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
            return []

    def generate_recipes(self, ingredients: List[Any], 
                         max_time: int = 20, 
                         dietary_restrictions: List[str] = None) -> List[Dict[str, Any]]:
        try:
            ingredients_list = []
            for ing in ingredients:
                if isinstance(ing, dict):
                    ingredients_list.append(ing.get('name', ''))
                elif isinstance(ing, str):
                    ingredients_list.append(ing)
            
            ingredients_text = ", ".join(filter(None, ingredients_list))
            if not ingredients_text:
                print("Seznam ingrediencí pro generování je prázdný.")
                return []

            prompt = self._create_recipe_prompt(ingredients_text, max_time, dietary_restrictions)
            response_str = self._call_gpt_api(prompt)
            return self._parse_recipes_response(response_str)
            
        except Exception as e:
            print(f"Chyba při generování receptů: {e}")
            return self._create_fallback_recipes()

    def _call_api(self, data: Dict[str, Any]) -> str:
        """
        Bezpečně zavolá OpenAI API a vrátí obsah odpovědi.
        Pokud obsah chybí nebo je None, vrátí prázdný string.
        """
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
            return "" # Vrací prázdný string, pokud struktura odpovědi není správná

        return content if content is not None else ""

    def _call_vision_api(self, encoded_image: str, prompt: str) -> str:
        data = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
                        }
                    ]
                }
            ],
            "max_tokens": 1000,
            "response_format": {"type": "json_object"}
        }
        return self._call_api(data)

    def _call_gpt_api(self, prompt: str) -> str:
        data = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": "Jsi expertní kuchař specializující se na rychlé a zdravé recepty."
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }
        return self._call_api(data)

    def _create_recipe_prompt(self, ingredients_text: str, max_time: int, 
                              dietary_restrictions: List[str]) -> str:
        restrictions_text = ""
        if dietary_restrictions:
            restrictions_text = f"\nDietní omezení: {', '.join(dietary_restrictions)}"
        
        return f"""
        Vytvoř 3-5 rychlých a zdravých receptů na základě těchto ingrediencí z ledničky: {ingredients_text}
        
        DŮLEŽITÉ: Počítej s tím, že doma máš k dispozici tyto běžné suroviny:
        Základní suroviny: těstoviny, rýže, brambory, mouka, cukr, med, olej, ocet, sojová omáčka, solamyl
        Zelenina a houby: šalotka, houby (čerstvé i sušené)
        Pesta a omáčky: bazalkové pesto, rajčatové pesto
        Mražené potraviny: mražená zelenina, mražené krevety
        Koření a bylinky: sůl, pepř, paprika, oregano, grilovací koření, chilli, česnek, cibule, bazalka, petržel, tymián, rozmarýn
        
        Požadavky:
        - Maximální čas přípravy: {max_time} minut
        - Žádné smažení, preferuj vaření, pečení, grilování, dušení
        - Zdravé recepty s minimem oleje a soli
        - Používej kombinaci ingrediencí z ledničky + běžných surovin doma
        - Respektuj dostupné spotřebiče: elektrický sporák, trouba, mikrovlnná trouba, horkovzdušná parní fritéza, mixér, tyčový mixér, elektrický kontaktní gril, toastovač
        {restrictions_text}
        
        Pro každý recept uveď: Název, čas přípravy, počet porcí, seznam ingrediencí s množstvím, postup, nutriční informace a tipy.
        Vrať výsledek jako JSON objekt s jedním klíčem "recipes", který obsahuje pole objektů.
        Každý objekt v poli musí mít klíče: name, prep_time, servings, ingredients, instructions, nutrition_info, cooking_tips.
        Vrať pouze validní JSON bez jakéhokoliv dalšího textu, komentářů nebo vysvětlení.
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
                
            ingredients = parsed_json.get('ingredients', [])
            
            valid_ingredients = []
            for ingredient in ingredients:
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
            print(f"Odpověď od OpenAI byla: {response_str}")
            return self._fallback_ingredients_parsing(response_str)

    def _parse_recipes_response(self, response_str: str) -> List[Dict[str, Any]]:
        try:
            parsed_json = self._parse_json_response(response_str)
            if not parsed_json:
                return self._create_fallback_recipes()
                
            recipes_from_api = parsed_json.get('recipes', [])
            
            valid_recipes = []
            for recipe in recipes_from_api:
                if not isinstance(recipe, dict):
                    print(f"Špatný typ receptu z OpenAI: {recipe} ({type(recipe)})")
                    continue

                try:
                    prep_time = int(recipe.get('prep_time', 0))
                except (ValueError, TypeError):
                    prep_time = 0
                new_recipe = {
                    'name': recipe.get('name', 'Recept bez názvu'),
                    'prep_time': prep_time,
                    'servings': recipe.get('servings', 1),
                    'ingredients': recipe.get('ingredients', []),
                    'instructions': recipe.get('instructions', []),
                    'nutrition_info': recipe.get('nutrition_info', {}),
                    'cooking_tips': recipe.get('cooking_tips', [])
                }
                
                new_recipe['tags'] = self._generate_recipe_tags(new_recipe)
                new_recipe['appliances'] = self._detect_appliances(new_recipe)
                
                valid_recipes.append(new_recipe)
                
            return valid_recipes
            
        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            print(f"Chyba při parsování receptů: {e}")
            print(f"Odpověď od OpenAI byla: {response_str}")
            return self._create_fallback_recipes()

    def _fallback_ingredients_parsing(self, response_str: str) -> List[Dict[str, Any]]:
        print("Používám záložní parsování ingrediencí.")
        ingredients = []
        # ... (zbytek logiky můžeš doplnit) ...
        return ingredients

    def _generate_recipe_tags(self, recipe: Dict) -> List[str]:
        tags = []
        try:
            prep_time = int(recipe.get('prep_time', 99))
        except (ValueError, TypeError):
            prep_time = 99
        if prep_time <= 20:
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
        return [
            {
                'name': 'Rychlá zeleninová polévka',
                'prep_time': 15,
                'servings': 2,
                'ingredients': [{'name': 'Zelenina z ledničky', 'amount': 'co dům dal'}, {'name': 'sůl, pepř', 'amount': 'na dochucení'}],
                'instructions': ['Nakrájejte zeleninu na kousky.', 'Zalijte vodou a vařte 15 minut.', 'Ochuťte solí a pepřem.'],
                'nutrition_info': {'calories': 150, 'protein': 5, 'carbs': 25, 'fat': 3},
                'cooking_tips': ['Můžete přidat koření podle chuti.'],
                'tags': ['rychlé', 'zeleninové', 'zdravé'],
                'appliances': ['elektrický sporák'],
            }
        ]
