# Fridge Recipe App 🍳

Aplikace pro generování rychlých a zdravých receptů na základě obsahu ledničky s podporou OpenAI AI.

## Funkce

- 📸 Nahrání fotografie obsahu ledničky
- 🤖 AI analýza pomocí OpenAI Vision API
- 🧠 Dynamické generování receptů pomocí OpenAI GPT
- ⏱️ Generování receptů do 20 minut
- 🥗 Zdravé recepty bez smažení
- 📱 Moderní a intuitivní rozhraní
- 🔄 Fallback mechanismus na lokální databázi

## AI Integrace

### OpenAI API
- **GPT-4 Vision**: Přesná analýza fotografií ledničky
- **GPT-4**: Generování unikátních receptů
- **Inteligentní filtrování**: Respektuje časové omezení a zdravé vaření

### Výhody AI
- 🎯 Neomezené recepty: Každý recept je unikátní
- 🔍 Přesná detekce: Skutečné rozpoznávání ingrediencí
- 🚀 Adaptivní: Přizpůsobuje se dostupným ingrediencím

## Dostupné spotřebiče

- Elektrický sporák
- Trouba
- Mikrovlnná trouba
- Horkovzdušná parní fritéza
- Mixér
- Tyčový mixér
- Elektrický kontaktní gril
- Toastovač

## Struktura projektu

```
fridge-recipe-app/
├── frontend/          # HTML/CSS/JS frontend
├── backend/           # Python Flask API
│   ├── services/     # Business logika
│   │   ├── openai_service.py  # OpenAI integrace
│   │   ├── image_analyzer.py  # AI analýza obrázků
│   │   └── recipe_generator.py # Generování receptů
│   └── routes/       # API endpoints
├── docs/             # Dokumentace
└── config.env        # Konfigurace (OpenAI API klíč)
```

## Rychlé spuštění

### 1. Instalace
```bash
git clone <repository>
cd fridge-recipe-app
pip install -r backend/requirements.txt
```

### 2. Konfigurace OpenAI (volitelné)
```bash
# Upravte config.env soubor s vaším OpenAI API klíčem
# Získejte klíč na: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Spuštění
```bash
# Backend
python start_backend.py

# Frontend (v novém terminálu)
python start_frontend.py
```

### 4. Použití
1. Otevřete `http://localhost:8000` v prohlížeči
2. Vyfotografujte obsah ledničky
3. Nahrajte fotografii
4. Získejte AI generované recepty!

## Režimy fungování

### 🚀 AI režim (s OpenAI API)
- Přesná analýza fotografií
- Neomezené množství unikátních receptů
- Inteligentní přizpůsobení ingrediencím

### 📚 Fallback režim (bez OpenAI)
- Simulace AI detekce
- 6 základních zdravých receptů
- Plná funkcionalita aplikace

## Náklady

- **OpenAI API**: ~$0.05-0.10 za analýzu
- **Fallback**: Zcela zdarma
- **Hosting**: Vlastní server nebo cloud 

Pokud je `ing` string, pak `ing.name`, `ing.amount` a `ing.unit` jsou `undefined`.

---

## Oprava

Musíme upravit renderování ingrediencí v detailu receptu tak, aby fungovalo pro oba případy:
- **Pokud je `ing` objekt:** zobrazit `ing.name`, `ing.amount`, `ing.unit`
- **Pokud je `ing` string:** zobrazit jen název

---

### **Navržená úprava (do metody showRecipeDetail):**

Najdi v `app.js` v metodě `showRecipeDetail` tento blok:
```js
${recipe.ingredients.map(ing => `
    <div class="recipe-ingredient">
        <strong>${ing.name}</strong> - ${ing.amount} ${ing.unit}
    </div>
`).join('')}
```

Nahraď ho tímto:
```js
${recipe.ingredients.map(ing => {
    if (typeof ing === 'string') {
        return `<div class="recipe-ingredient"><strong>${ing}</strong></div>`;
    } else {
        return `<div class="recipe-ingredient"><strong>${ing.name ?? ''}</strong>${ing.amount ? ' - ' + ing.amount : ''} ${ing.unit ?? ''}</div>`;
    }
}).join('')}
```

---
