from flask import Flask
from .models import db

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')
    
    # Initialize database
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()

    # Import routes
    from . import routes
    app.register_blueprint(routes.bp)

    return app