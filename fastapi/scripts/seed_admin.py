'''
run this once to create the first admin account.

usage:
    cd fastapi
    docker compose exec fastapi python -m scripts.seed_admin

what it does:
    - checks if any admin already exists
    - if not, creates one with the email and password from .env
    - safe to run more than once (it will skip if admin already exists)

required .env variables:
    SEED_ADMIN_EMAIL     = your-admin-email-here
    SEED_ADMIN_PASSWORD  = your-strong-password-here
    SEED_ADMIN_USERNAME  = your-admin-username-here
'''

import os
import sys

# add the fastapi folder to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from dotenv import load_dotenv

load_dotenv()

from app.db import SessionLocal
from app.models.user import User


def hash_password(plain: str) -> str:
    '''hash password using bcrypt, same as security.py'''
    pwd_bytes = plain.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def seed():
    # read from .env
    email    = os.getenv("SEED_ADMIN_EMAIL", "")
    password = os.getenv("SEED_ADMIN_PASSWORD", "")
    username = os.getenv("SEED_ADMIN_USERNAME", "")

    if not password:
        print("error: SEED_ADMIN_PASSWORD is not set in .env")
        sys.exit(1)

    db = SessionLocal()
    try:
        # skip if any admin already exists
        existing = db.query(User).filter(User.role == "admin").first()
        if existing:
            print(f"admin already exists (username: {existing.username}), skipping")
            return

        # also check if email is already taken by another role
        email_taken = db.query(User).filter(User.email == email).first()
        if email_taken:
            print(f"email {email} is already registered as role={email_taken.role}")
            print("updating role to admin...")
            email_taken.role = "admin"
            db.commit()
            print("done")
            return

        admin = User(
            username = username,
            email = email,
            hashed_password = hash_password(password),
            full_name = "Admin",
            role = "admin",
            is_active = True,
            email_sent = False,
        )
        db.add(admin)
        db.commit()
        print(f"admin created: username={username}, email={email}")
        print("please change the password after first login")

    finally:
        db.close()

if __name__ == "__main__":
    seed()