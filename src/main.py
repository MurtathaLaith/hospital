import os
import sys
# DON'T CHANGE: Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import bcrypt
from src.models.user import db, User
from src.models.department import Department
from src.models.doctor import Doctor
from src.models.patient import Patient
from src.models.visit import Visit
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.central import central_bp
from src.routes.secretary import secretary_bp
from src.routes.patient import patient_bp
from src.routes.frontend import frontend_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-change-in-production'

# Enable CORS for all routes
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize JWT
jwt = JWTManager(app)

def create_app():
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Create default users if they don't exist
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                password_hash=bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                role='central'
            )
            db.session.add(admin_user)
            
        if not User.query.filter_by(username='secretary1').first():
            secretary_user = User(
                username='secretary1',
                password_hash=bcrypt.hashpw('secretary123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                role='secretary'
            )
            db.session.add(secretary_user)
            
        db.session.commit()
        print("Default users created:")
        print("Admin: username=admin, password=admin123")
        print("Secretary: username=secretary1, password=secretary123")

    # Register blueprints
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(central_bp, url_prefix='/api/central')
    app.register_blueprint(secretary_bp, url_prefix='/api/secretary')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')
    app.register_blueprint(frontend_bp)  # No prefix for frontend routes
    
    return app

if __name__ == '__main__':
    # Initialize the app
    create_app()
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=True)

