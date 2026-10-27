from app.routes.auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.bus_routes import bus_bp
from app.routes.bunk_routes import bunk_bp
from app.routes.fuel_routes import fuel_bp
from app.routes.approval_routes import approval_bp
from app.routes.analytics_routes import analytics_bp
from app.routes.report_routes import report_bp
from app.routes.audit_routes import audit_bp
from app.routes.bill_routes import bill_bp
from app.routes.driver_routes import driver_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(bus_bp)
    app.register_blueprint(bunk_bp)
    app.register_blueprint(fuel_bp)
    app.register_blueprint(approval_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(bill_bp)
    app.register_blueprint(driver_bp)
