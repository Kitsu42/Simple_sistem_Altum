from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, name: str, email: str, password: str, role: UserRole = UserRole.comprador) -> User:
    user = User(
        name=name,
        email=email,
        hashed_password=get_password_hash(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.id.asc()).all()
