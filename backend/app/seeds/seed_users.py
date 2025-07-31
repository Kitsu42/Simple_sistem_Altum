from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import User, Role, Permission
from app.core.security import get_password_hash

def seed_data():
    db: Session = SessionLocal()

    # Criação de permissões, se não existirem
    permissions = ["create", "read", "update", "delete"]
    for action in permissions:
        existing = db.query(Permission).filter_by(action=action).first()
        if not existing:
            db.add(Permission(action=action))
    db.commit()

    # Criação de roles
    roles_data = ["admin", "operador"]
    roles_dict = {}
    for role_name in roles_data:
        role = db.query(Role).filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            db.add(role)
            db.commit()
        roles_dict[role_name] = role

    # Criação de usuários
    users_data = [
        {
            "email": "admin@example.com",
            "password": "admin123",
            "role": "admin"
        },
        {
            "email": "operador@example.com",
            "password": "123456",
            "role": "operador"
        }
    ]

    for user in users_data:
        existing_user = db.query(User).filter_by(email=user["email"]).first()
        if not existing_user:
            db.add(User(
                email=user["email"],
                hashed_password=get_password_hash(user["password"]),
                is_active=True,
                role_id=roles_dict[user["role"]].id
            ))
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_data()
