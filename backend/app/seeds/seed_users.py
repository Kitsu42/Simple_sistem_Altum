from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import models
from app.core.security import get_password_hash

def seed_data():
    db: Session = SessionLocal()

    # Criação de permissões
    perm_create = models.Permission(action="create")
    perm_read = models.Permission(action="read")
    perm_update = models.Permission(action="update")
    perm_delete = models.Permission(action="delete")

    db.add_all([perm_create, perm_read, perm_update, perm_delete])
    db.commit()

    # Criação de roles
    admin_role = models.Role(name="admin")
    user_role = models.Role(name="operador")
    db.add_all([admin_role, user_role])
    db.commit()

    # Criação de usuários
    admin_user = models.User(
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        role_id=admin_role.id
    )

    operator_user = models.User(
        email="operador@example.com",
        hashed_password=get_password_hash("123456"),
        is_active=True,
        role_id=user_role.id
    )

    db.add_all([admin_user, operator_user])
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_data()