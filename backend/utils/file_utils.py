import os
from werkzeug.utils import secure_filename

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_image(file, filename, upload_folder):
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return file_path

def cleanup_old_files(upload_folder, max_age_hours=24):
    import time
    from datetime import datetime, timedelta
    
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(hours=max_age_hours)
    
    if not os.path.exists(upload_folder):
        return
    
    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        file_time = datetime.fromtimestamp(os.path.getctime(file_path))
        
        if file_time < cutoff_time:
            try:
                os.remove(file_path)
                print(f"Smazán starý soubor: {filename}")
            except OSError as e:
                print(f"Chyba při mazání souboru {filename}: {e}")

def get_file_size_mb(file_path):
    if not os.path.exists(file_path):
        return 0
    
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024) 