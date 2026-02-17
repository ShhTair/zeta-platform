#!/usr/bin/env python3
"""
Initialize database and create super admin user
"""
import sys
from app.core.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.core.security import get_password_hash


def init_database():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def create_super_admin(email: str, password: str):
    """Create super admin user"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"✗ User with email {email} already exists")
            return False
        
        # Create super admin
        admin = User(
            email=email,
            password_hash=get_password_hash(password),
            role=UserRole.SUPER_ADMIN
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"✓ Super admin created successfully")
        print(f"  Email: {admin.email}")
        print(f"  Role: {admin.role.value}")
        print(f"  ID: {admin.id}")
        return True
    except Exception as e:
        print(f"✗ Error creating super admin: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    print("=" * 50)
    print("ZETA Platform - Database Initialization")
    print("=" * 50)
    
    # Initialize database
    try:
        init_database()
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        sys.exit(1)
    
    # Create super admin
    print("\nCreating super admin user...")
    email = input("Enter email (default: admin@zeta.local): ").strip() or "admin@zeta.local"
    password = input("Enter password (default: admin123): ").strip() or "admin123"
    
    if create_super_admin(email, password):
        print("\n" + "=" * 50)
        print("Setup completed successfully!")
        print("=" * 50)
        print("\nYou can now start the API server:")
        print("  uvicorn app.main:app --reload")
        print("\nOr run migrations:")
        print("  alembic upgrade head")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
