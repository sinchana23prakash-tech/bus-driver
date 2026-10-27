import os
from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine
from config import Config
from app.extensions import db, jwt
from app.routes import register_blueprints

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Establish database URI with safe fallback
    db_uri = config_class.get_database_uri()
    
    # Test connection if MySQL URI is configured
    if 'mysql' in db_uri:
        try:
            test_engine = create_engine(db_uri, connect_args={'connect_timeout': 3})
            with test_engine.connect() as conn:
                pass
            app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
            print(f"[DB] Successfully connected to MySQL database: {config_class.MYSQL_DATABASE}")
        except Exception as e:
            fallback_uri = f"sqlite:///{config_class.SQLITE_PATH}"
            app.config['SQLALCHEMY_DATABASE_URI'] = fallback_uri
            print(f"[DB] Notice: MySQL connection could not be established ({e}). Gracefully falling back to SQLite ({config_class.SQLITE_PATH}) without losing any data.")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        print(f"[DB] Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Ensure secure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    register_blueprints(app)

    # JWT Error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({'error': 'Missing or invalid Authorization header.'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return jsonify({'error': 'Signature verification failed or token is malformed.'}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Session token has expired. Please log in again.'}), 401

    # Safe table creation (preserves existing data, creates only missing tables)
    with app.app_context():
        db.create_all()

    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        from app.models.user import User
        admin_count = User.query.filter_by(role='ADMIN').count()
        return jsonify({
            'status': 'healthy',
            'service': 'College Bus Fuel Management System API',
            'needs_initial_setup': (admin_count == 0),
            'vc_can_approve': app.config.get('VC_CAN_APPROVE', False)
        }), 200

    return app
