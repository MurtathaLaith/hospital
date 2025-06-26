from flask import Blueprint, send_from_directory, current_app
import os

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
@frontend_bp.route('/<path:path>')
def serve_frontend(path=''):
    """Serve the React frontend"""
    static_folder = os.path.join(current_app.root_path, 'static')
    
    # If path is empty or doesn't exist, serve index.html
    if not path or not os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, 'index.html')
    
    return send_from_directory(static_folder, path)

