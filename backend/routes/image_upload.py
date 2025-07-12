from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from ..services.image_analyzer import ImageAnalyzer
from ..utils.file_utils import allowed_file, save_image

image_bp = Blueprint('image', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

@image_bp.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Nebyl nalezen soubor'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'Nebyl vybrán žádný soubor'}), 400
        
        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({'error': 'Nepodporovaný formát souboru'}), 400
        
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        file_path = save_image(file, unique_filename, current_app.config['UPLOAD_FOLDER'])
        
        analyzer = ImageAnalyzer()
        ingredients = analyzer.analyze_fridge_content(file_path)
        
        return jsonify({
            'message': 'Obrázek byl úspěšně nahrán a analyzován',
            'filename': unique_filename,
            'ingredients': ingredients,
            'upload_time': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Chyba při nahrávání: {str(e)}'}), 500

@image_bp.route('/analyze/<filename>', methods=['GET'])
def analyze_image(filename):
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Soubor nebyl nalezen'}), 404
        
        analyzer = ImageAnalyzer()
        ingredients = analyzer.analyze_fridge_content(file_path)
        
        return jsonify({
            'filename': filename,
            'ingredients': ingredients,
            'analysis_time': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Chyba při analýze: {str(e)}'}), 500 