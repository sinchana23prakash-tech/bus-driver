import sys
import argparse
import getpass
from app import create_app
from app.models.user import User
from app.extensions import db
from app.utils.auth_helpers import log_audit_action

def setup_admin():
    parser = argparse.ArgumentParser(description="Secure Administrator Initialization for College Bus Fuel System")
    parser.add_argument("--username", help="Administrator username")
    parser.add_argument("--email", help="Administrator official email")
    parser.add_argument("--password", help="Administrator secure password")
    parser.add_argument("--name", help="Administrator full name")
    parser.add_argument("--phone", help="Contact phone number")
    args = parser.parse_args()

    app = create_app()

    with app.app_context():
        existing_admins = User.query.filter_by(role='ADMIN').count()
        print("=============================================================")
        print(" COLLEGE BUS FUEL MANAGEMENT SYSTEM - ADMIN SETUP")
        print("=============================================================")
        if existing_admins > 0:
            print(f"[!] Notice: {existing_admins} Administrator account(s) already exist.")
            proceed = input("Do you want to create an additional Administrator? (y/N): ").strip().lower()
            if proceed not in ('y', 'yes'):
                print("Setup aborted.")
                sys.exit(0)

        username = args.username
        if not username:
            username = input("Enter admin username: ").strip()

        email = args.email
        if not email:
            email = input("Enter admin official email: ").strip().lower()

        full_name = args.name
        if not full_name:
            full_name = input("Enter admin full name: ").strip()

        phone = args.phone
        if not phone:
            phone = input("Enter contact phone number (optional): ").strip()

        password = args.password
        if not password:
            while True:
                password = getpass.getpass("Enter secure password (min 8 chars): ")
                if len(password) < 8:
                    print("Error: Password must be at least 8 characters long.")
                    continue
                confirm = getpass.getpass("Confirm password: ")
                if password != confirm:
                    print("Error: Passwords do not match. Please try again.")
                    continue
                break

        # Check existing user
        if User.query.filter((User.username == username) | (User.email == email)).first():
            print(f"Error: User with username '{username}' or email '{email}' already exists.")
            sys.exit(1)

        admin_user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone_number=phone,
            role='ADMIN',
            is_active=True
        )
        admin_user.set_password(password)
        db.session.add(admin_user)
        db.session.commit()

        log_audit_action(
            actor_user=admin_user,
            action='ADMIN_INITIALIZED_VIA_CLI',
            entity_type='USER',
            entity_id=admin_user.id,
            details=f"Admin account created via secure CLI initialization: {username}"
        )

        print("\n[SUCCESS] Administrator account successfully configured!")
        print(f"Username: {username}")
        print(f"Email:    {email}")
        print(f"Role:     ADMIN")
        print("You can now log in to the React Web Dashboard or manage fleet accounts.\n")

if __name__ == '__main__':
    setup_admin()
