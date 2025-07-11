from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv('config.env')

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    from routes.image_upload import image_bp
    from routes.recipe_generator import recipe_bp
    
    app.register_blueprint(image_bp, url_prefix='/api/image')
    app.register_blueprint(recipe_bp, url_prefix='/api/recipes')
    
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Fridge Recipe App API is running'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)

# Create app instance for gunicorn
app = create_app()
