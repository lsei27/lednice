/**
 * Fridge Recipe App - Frontend JavaScript
 */

class FridgeRecipeApp {
    constructor() {
        this.apiBaseUrl = 'https://lednice.onrender.com/api';
        this.selectedFile = null;
        this.ingredients = [];
        this.recipes = [];
        
        this.initializeElements();
        this.bindEvents();
    }
    
    initializeElements() {
        // DOM elements
        this.uploadArea = document.getElementById('uploadArea');
        this.imageInput = document.getElementById('imageInput');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.newPhotoBtn = document.getElementById('newPhotoBtn');
        
        // Sections
        this.uploadSection = document.getElementById('uploadSection');
        this.loadingSection = document.getElementById('loadingSection');
        this.resultsSection = document.getElementById('resultsSection');
        
        // Results elements
        this.ingredientsGrid = document.getElementById('ingredientsGrid');
        this.recipesGrid = document.getElementById('recipesGrid');
        
        // Modal elements
        this.recipeModal = document.getElementById('recipeModal');
        this.modalClose = document.getElementById('modalClose');
        this.modalRecipeName = document.getElementById('modalRecipeName');
        this.modalBody = document.getElementById('modalBody');
    }
    
    bindEvents() {
        // Upload area events
        this.uploadArea.addEventListener('click', () => this.imageInput.click());
        this.uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        this.uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        this.uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        
        // File input event
        this.imageInput.addEventListener('change', this.handleFileSelect.bind(this));
        
        // Button events
        this.uploadBtn.addEventListener('click', this.uploadImage.bind(this));
        this.newPhotoBtn.addEventListener('click', this.resetToUpload.bind(this));
        
        // Modal events
        this.modalClose.addEventListener('click', this.closeModal.bind(this));
        this.recipeModal.addEventListener('click', (e) => {
            if (e.target === this.recipeModal) {
                this.closeModal();
            }
        });
    }
    
    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }
    
    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.handleFile(file);
        }
    }
    
    handleFile(file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showError('Prosím vyberte obrázek.');
            return;
        }
        
        // Validate file size (max 16MB)
        if (file.size > 16 * 1024 * 1024) {
            this.showError('Soubor je příliš velký. Maximální velikost je 16MB.');
            return;
        }
        
        this.selectedFile = file;
        this.uploadBtn.disabled = false;
        
        // Show preview
        this.showImagePreview(file);
    }
    
    showImagePreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.uploadArea.innerHTML = `
                <div class="upload-content">
                    <img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px; border-radius: 10px;">
                    <p>${file.name}</p>
                    <p class="upload-hint">Klikněte pro změnu</p>
                </div>
            `;
        };
        reader.readAsDataURL(file);
    }
    
    async uploadImage() {
        if (!this.selectedFile) {
            this.showError('Prosím vyberte obrázek.');
            return;
        }
        
        this.showLoading();
        
        try {
            const formData = new FormData();
            formData.append('image', this.selectedFile);
            
            const response = await fetch(`${this.apiBaseUrl}/image/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.ingredients = data.ingredients;
            
            // Generate recipes
            await this.generateRecipes();
            
            this.showResults();
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showError('Chyba při nahrávání obrázku. Zkuste to prosím znovu.');
            this.hideLoading();
        }
    }
    
    async generateRecipes() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/recipes/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ingredients: this.ingredients,
                    max_time: 20,
                    dietary_restrictions: []
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.recipes = data.recipes;
            
        } catch (error) {
            console.error('Recipe generation error:', error);
            this.showError('Chyba při generování receptů.');
        }
    }
    
    showLoading() {
        this.uploadSection.style.display = 'none';
        this.loadingSection.style.display = 'flex';
        this.resultsSection.style.display = 'none';
    }
    
    hideLoading() {
        this.loadingSection.style.display = 'none';
    }
    
    showResults() {
        this.hideLoading();
        this.resultsSection.style.display = 'block';
        
        this.renderIngredients();
        this.renderRecipes();
        
        // Add fade-in animation
        this.resultsSection.classList.add('fade-in');
    }
    
    renderIngredients() {
        this.ingredientsGrid.innerHTML = '';
        
        this.ingredients.forEach(ingredient => {
            const ingredientCard = document.createElement('div');
            ingredientCard.className = 'ingredient-card fade-in';
            
            const icon = this.getIngredientIcon(ingredient.category);
            
            ingredientCard.innerHTML = `
                <div class="ingredient-icon">
                    <i class="${icon}"></i>
                </div>
                <div class="ingredient-name">${ingredient.name}</div>
                <div class="ingredient-category">${ingredient.category}</div>
            `;
            
            this.ingredientsGrid.appendChild(ingredientCard);
        });
    }
    
    renderRecipes() {
        this.recipesGrid.innerHTML = '';
        
        this.recipes.forEach(recipe => {
            const recipeCard = document.createElement('div');
            recipeCard.className = 'recipe-card fade-in';
            recipeCard.addEventListener('click', () => this.showRecipeDetail(recipe));
            
            const availability = recipe.ingredient_availability;
            const availabilityText = `${availability.available_count}/${availability.total_count} ingrediencí dostupných`;
            
            recipeCard.innerHTML = `
                <div class="recipe-header">
                    <div class="recipe-name">${recipe.name}</div>
                    <div class="recipe-time">${recipe.prep_time} min</div>
                </div>
                <div class="recipe-tags">
                    ${recipe.tags.map(tag => `<span class="recipe-tag">${tag}</span>`).join('')}
                </div>
                <div class="recipe-availability">${availabilityText}</div>
            `;
            
            this.recipesGrid.appendChild(recipeCard);
        });
    }
    
    showRecipeDetail(recipe) {
        this.modalRecipeName.textContent = recipe.name;
        
        const availability = recipe.ingredient_availability;
        const nutrition = recipe.nutrition_info;
        
        this.modalBody.innerHTML = `
            <div class="recipe-detail-section">
                <h4>Ingredience</h4>
                <div class="recipe-ingredients">
                    ${recipe.ingredients.map(ing => `
                        <div class="recipe-ingredient">
                            <strong>${ing.name}</strong> - ${ing.amount} ${ing.unit}
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="recipe-detail-section">
                <h4>Postup přípravy</h4>
                <ol class="recipe-instructions">
                    ${recipe.instructions.map(instruction => `
                        <li class="recipe-instruction">${instruction}</li>
                    `).join('')}
                </ol>
            </div>
            
            <div class="recipe-detail-section">
                <h4>Nutriční informace (na porci)</h4>
                <div class="recipe-ingredients">
                    <div class="recipe-ingredient">
                        <strong>Kalorie:</strong> ${nutrition.calories_per_serving} kcal
                    </div>
                    <div class="recipe-ingredient">
                        <strong>Bílkoviny:</strong> ${nutrition.protein}
                    </div>
                    <div class="recipe-ingredient">
                        <strong>Sacharidy:</strong> ${nutrition.carbs}
                    </div>
                    <div class="recipe-ingredient">
                        <strong>Tuky:</strong> ${nutrition.fat}
                    </div>
                    <div class="recipe-ingredient">
                        <strong>Vláknina:</strong> ${nutrition.fiber}
                    </div>
                </div>
            </div>
            
            ${recipe.cooking_tips ? `
                <div class="recipe-detail-section">
                    <h4>Tipy pro přípravu</h4>
                    <ul class="recipe-instructions">
                        ${recipe.cooking_tips.map(tip => `
                            <li class="recipe-instruction">${tip}</li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
        
        this.recipeModal.classList.add('active');
    }
    
    closeModal() {
        this.recipeModal.classList.remove('active');
    }
    
    resetToUpload() {
        this.selectedFile = null;
        this.ingredients = [];
        this.recipes = [];
        
        // Reset upload area
        this.uploadArea.innerHTML = `
            <div class="upload-content">
                <i class="fas fa-cloud-upload-alt"></i>
                <p>Klikněte pro nahrání fotografie</p>
                <p class="upload-hint">nebo přetáhněte soubor sem</p>
            </div>
        `;
        
        this.uploadBtn.disabled = true;
        
        // Show upload section
        this.uploadSection.style.display = 'flex';
        this.loadingSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
    }
    
    getIngredientIcon(category) {
        const icons = {
            'zelenina': 'fas fa-carrot',
            'ovoce': 'fas fa-apple-alt',
            'maso': 'fas fa-drumstick-bite',
            'mléčné': 'fas fa-cheese',
            'vejce': 'fas fa-egg',
            'těstoviny': 'fas fa-bread-slice',
            'rýže': 'fas fa-seedling',
            'luštěniny': 'fas fa-seedling',
            'koření': 'fas fa-pepper-hot',
            'ostatní': 'fas fa-utensils'
        };
        
        return icons[category] || icons['ostatní'];
    }
    
    showError(message) {
        // Simple error notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #e53e3e;
            color: white;
            padding: 1rem 2rem;
            border-radius: 10px;
            z-index: 1001;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FridgeRecipeApp();
}); 