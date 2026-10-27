from getpass import getpass
from app import create_app
from app.models.user import User
from app.extensions import db

app = create_app()

with app.app_context():
    admin = User.query.filter_by(username="admin").first()

    if admin is None:
        print("Admin account not found. No changes made.")
    else:
        password = getpass("Enter new admin password (minimum 8 characters): ")
        confirm = getpass("Confirm new admin password: ")

        if len(password) < 8:
            print("Password must be at least 8 characters.")
        elif password != confirm:
            print("Passwords do not match. No changes made.")
        else:
            admin.set_password(password)
            db.session.commit()
            print("Admin password reset successfully.")