from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def init_db():
    # Cria as tabelas
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Usuários de teste
    test_users = [
        {"username": "admin", "email": "admin@example.com", "password": "admin123", "role": "admin"},
        {"username": "manager", "email": "manager@example.com", "password": "manager123", "role": "manager"},
        {"username": "user", "email": "user@example.com", "password": "user123", "role": "user"},
    ]

    for u in test_users:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if not existing:
            user = User(
                username=u["username"],
                email=u["email"],
                hashed_password=get_password_hash(u["password"]),
                role=u["role"]
            )
            db.add(user)

    db.commit()
    db.close()
    print("✅ Usuários de teste criados com sucesso!")


if __name__ == "__main__":
    init_db()
