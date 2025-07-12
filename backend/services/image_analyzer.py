import cv2
import numpy as np
from PIL import Image
import os
import json
from typing import List, Dict, Any
from .recipe_generator import OpenAIService

class ImageAnalyzer:
    def __init__(self):
        self.common_ingredients = {
            'zelenina': ['mrkev', 'cibule', 'česnek', 'paprika', 'rajčata', 'okurka', 
                        'salát', 'špenát', 'brokolice', 'květák', 'zelí', 'brambory'],
            'ovoce': ['jablka', 'banány', 'pomeranče', 'citrony', 'limetky', 'hrušky'],
            'maso': ['kuřecí prsa', 'vepřové maso', 'hovězí maso', 'ryby', 'losos', 'treska'],
            'mléčné': ['mléko', 'jogurt', 'sýr', 'tvaroh', 'smetana', 'máslo'],
            'vejce': ['vajíčka'],
            'těstoviny': ['špagety', 'penne', 'fusilli', 'tagliatelle'],
            'rýže': ['rýže', 'basmati', 'jasmínová rýže'],
            'luštěniny': ['čočka', 'fazole', 'cizrna', 'hrách'],
            'koření': ['sůl', 'pepř', 'oregano', 'bazalka', 'tymián', 'rozmarýn']
        }
        
        try:
            self.openai_service = OpenAIService()
            self.use_openai = True
        except Exception as e:
            print(f"OpenAI služba není dostupná: {e}")
            self.use_openai = False
    
    def analyze_fridge_content(self, image_path: str) -> List[Dict[str, Any]]:
        try:
            if self.use_openai:
                print("🔍 Používám OpenAI Vision API pro analýzu obrázku...")
                return self.openai_service.analyze_fridge_image(image_path)
            
            print("🔍 Používám simulaci AI detekce...")
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Nepodařilo se načíst obrázek")
            
            processed_image = self._preprocess_image(image)
            detected_objects = self._detect_objects(processed_image)
            ingredients = self._classify_ingredients(detected_objects)
            
            return ingredients
            
        except Exception as e:
            print(f"Chyba při analýze obrázku: {e}")
            return []
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        height, width = rgb_image.shape[:2]
        max_size = 1024
        
        if max(height, width) > max_size:
            scale = max_size / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            rgb_image = cv2.resize(rgb_image, (new_width, new_height))
        
        normalized = rgb_image.astype(np.float32) / 255.0
        return normalized
    
    def _detect_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        detected_objects = []
        height, width = image.shape[:2]
        
        regions = [
            {'x': 0, 'y': 0, 'w': width//2, 'h': height//2, 'confidence': 0.8},
            {'x': width//2, 'y': 0, 'w': width//2, 'h': height//2, 'confidence': 0.7},
            {'x': 0, 'y': height//2, 'w': width//2, 'h': height//2, 'confidence': 0.9},
            {'x': width//2, 'y': height//2, 'w': width//2, 'h': height//2, 'confidence': 0.6}
        ]
        
        for region in regions:
            detected_objects.append({
                'region': region,
                'ingredients': self._simulate_ingredient_detection(region)
            })
        
        return detected_objects
    
    def _simulate_ingredient_detection(self, region: Dict[str, Any]) -> List[str]:
        import random
        
        all_ingredients = []
        for category in self.common_ingredients.values():
            all_ingredients.extend(category)
        
        num_ingredients = random.randint(3, 7)
        detected = random.sample(all_ingredients, min(num_ingredients, len(all_ingredients)))
        
        return detected
    
    def _classify_ingredients(self, detected_objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        ingredients = []
        
        for obj in detected_objects:
            for ingredient_name in obj['ingredients']:
                category = self._get_ingredient_category(ingredient_name)
                
                ingredients.append({
                    'name': ingredient_name,
                    'category': category,
                    'confidence': obj['region']['confidence'],
                    'quantity': 'dostupné',
                    'freshness': 'čerstvé'
                })
        
        unique_ingredients = []
        seen_names = set()
        
        for ingredient in ingredients:
            if ingredient['name'] not in seen_names:
                unique_ingredients.append(ingredient)
                seen_names.add(ingredient['name'])
        
        return unique_ingredients
    
    def _get_ingredient_category(self, ingredient_name: str) -> str:
        for category, ingredients in self.common_ingredients.items():
            if ingredient_name.lower() in [ing.lower() for ing in ingredients]:
                return category
        return 'ostatní' 