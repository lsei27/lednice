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
            
            Vrať výsledek jako JSON pole objektů s klíči: name, category, quantity, freshness
            """
            
            response = self._call_vision_api(encoded_image, prompt)
            return self._parse_ingredients_response(response)
            
        except Exception as e:
            print(f"Chyba při analýze obrázku: {e}")
            return []
    
    def generate_recipes(self, ingredients: List[Dict[str, Any]], 
                        max_time: int = 20, 
                        dietary_restrictions: List[str] = None) -> List[Dict[str, Any]]:
        try:
            ingredients_text = ", ".join([ing['name'] for ing in ingredients])
            prompt = self._create_recipe_prompt(ingredients_text, max_time, dietary_restrictions)
            response = self._call_gpt_api(prompt)
            return self._parse_recipes_response(response)
            
        except Exception as e:
            print(f"Chyba při generování receptů: {e}")
            return []
    
    def _call_vision_api(self, encoded_image: str, prompt: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
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
            "max_tokens": 1000
        }
        
        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
        
        if response.status_code != 200:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
        
        return response.json()['choices'][0]['message']['content']
    
    def _call_gpt_api(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
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
            "temperature": 0.7
        }
        
        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
        
        if response.status_code != 200:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
        
        return response.json()['choices'][0]['message']['content']
    
    def _create_recipe_prompt(self, ingredients_text: str, max_time: int, 
                             dietary_restrictions: List[str]) -> str:
        restrictions_text = ""
        if dietary_restrictions:
            restrictions_text = f"\nDietní omezení: {', '.join(dietary_restrictions)}"
        
        prompt = f"""
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
        
        Pro každý recept uveď:
        - Název receptu
        - Čas přípravy v minutách
        - Počet porcí
        - Seznam ingrediencí s množstvím (označ, které jsou z ledničky a které běžné doma)
        - Postup přípravy (kroky)
        - Nutriční informace (kalorie, bílkoviny, sacharidy, tuky na porci)
        - Tipy pro přípravu
        
        Vrať výsledek jako JSON pole objektů s klíči: name, prep_time, servings, ingredients, instructions, nutrition_info, cooking_tips
        """
        
        return prompt
    
    def _parse_ingredients_response(self, response: str) -> List[Dict[str, Any]]:
        try:
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            ingredients = json.loads(cleaned_response)
            
            if not isinstance(ingredients, list):
                ingredients = [ingredients]
            
            valid_ingredients = []
            for ingredient in ingredients:
                if not isinstance(ingredient, dict) or 'name' not in ingredient:
                    continue
                    
                valid_ingredient = {
                    'name': ingredient.get('name', 'Neznámá ingredience'),
                    'category': ingredient.get('category', 'ostatní'),
                    'quantity': ingredient.get('quantity', 'dostupné'),
                    'freshness': ingredient.get('freshness', 'čerstvé')
                }
                
                valid_ingredients.append(valid_ingredient)
            
            return valid_ingredients
            
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"Chyba při parsování ingrediencí: {e}")
            return self._fallback_ingredients_parsing(response)
    
    def _parse_recipes_response(self, response: str) -> List[Dict[str, Any]]:
        try:
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            recipes = json.loads(cleaned_response)
            
            if not isinstance(recipes, list):
                recipes = [recipes]
            
            enriched_recipes = []
            for recipe in recipes:
                if not isinstance(recipe, dict) or 'name' not in recipe:
                    continue
                    
                enriched_recipe = {
                    'id': f"ai_{hash(recipe.get('name', '')) % 10000}",
                    'name': recipe.get('name', 'Neznámý recept'),
                    'prep_time': recipe.get('prep_time', 15),
                    'servings': recipe.get('servings', 2),
                    'difficulty': 'snadné' if recipe.get('prep_time', 15) <= 15 else 'střední',
                    'ingredients': recipe.get('ingredients', []),
                    'instructions': recipe.get('instructions', []),
                    'nutrition_info': recipe.get('nutrition_info', {}),
                    'cooking_tips': recipe.get('cooking_tips', [])
                }
                
                enriched_recipe['tags'] = self._generate_recipe_tags(enriched_recipe)
                enriched_recipe['appliances'] = self._detect_appliances(enriched_recipe)
                enriched_recipe['ingredient_availability'] = {
                    'available_count': len(enriched_recipe['ingredients']),
                    'total_count': len(enriched_recipe['ingredients']),
                    'availability_percentage': 100,
                    'missing_ingredients': []
                }
                
                enriched_recipes.append(enriched_recipe)
            
            return enriched_recipes
            
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"Chyba při parsování receptů: {e}")
            return self._create_fallback_recipes()
    
    def _fallback_ingredients_parsing(self, response: str) -> List[Dict[str, Any]]:
        ingredients = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ':' in line:
                name = line.split(':')[0].strip()
                category = 'ostatní'
                
                if any(word in name.lower() for word in ['mrkev', 'cibule', 'paprika', 'rajče', 'okurka']):
                    category = 'zelenina'
                elif any(word in name.lower() for word in ['kuřecí', 'vepřové', 'hovězí']):
                    category = 'maso'
                elif any(word in name.lower() for word in ['mléko', 'sýr', 'jogurt']):
                    category = 'mléčné'
                
                ingredients.append({
                    'name': name,
                    'category': category,
                    'quantity': 'dostupné',
                    'freshness': 'čerstvé'
                })
        
        return ingredients
    
    def _generate_recipe_tags(self, recipe: Dict) -> List[str]:
        tags = []
        
        if recipe.get('prep_time', 0) <= 15:
            tags.append('rychlé')
        if recipe.get('prep_time', 0) <= 10:
            tags.append('ultrarychlé')
        
        if any('zelenina' in ing.lower() for ing in recipe.get('ingredients', [])):
            tags.append('zeleninové')
        if any('kuřecí' in ing.lower() for ing in recipe.get('ingredients', [])):
            tags.append('kuřecí')
        if any('ryba' in ing.lower() for ing in recipe.get('ingredients', [])):
            tags.append('rybí')
        
        tags.append('zdravé')
        
        return tags
    
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
        
        return appliances
    
    def _create_fallback_recipes(self) -> List[Dict[str, Any]]:
        return [
            {
                'id': 'fallback_1',
                'name': 'Rychlá zeleninová polévka',
                'prep_time': 15,
                'servings': 2,
                'difficulty': 'snadné',
                'ingredients': ['zelenina z ledničky', 'brambory', 'cibule', 'česnek', 'sůl', 'pepř'],
                'instructions': [
                    'Nakrájejte zeleninu na kousky',
                    'Osmahněte cibuli a česnek',
                    'Přidejte zeleninu a brambory',
                    'Zalijte vodou a vařte 10 minut',
                    'Ochuťte solí a pepřem'
                ],
                'nutrition_info': {'calories': 150, 'protein': 5, 'carbs': 25, 'fat': 3},
                'cooking_tips': ['Můžete přidat koření podle chuti'],
                'tags': ['rychlé', 'zeleninové', 'zdravé'],
                'appliances': ['elektrický sporák'],
                'ingredient_availability': {
                    'available_count': 6,
                    'total_count': 6,
                    'availability_percentage': 100,
                    'missing_ingredients': []
                }
            }
        ] 
