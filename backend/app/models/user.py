from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Enum
from app.core.db import Base
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    gestor = "gestor"
    comprador = "comprador"
    leitor = "leitor"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.comprador, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
