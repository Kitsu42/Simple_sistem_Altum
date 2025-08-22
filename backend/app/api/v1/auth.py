from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core import security, db
from app.schemas.user import UserLogin, Token
from app.crud import users

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login(data: UserLogin, session: Session = Depends(db.get_db)):
    user = users.get_user_by_email(session, email=data.username)
    if not user or not security.verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    access_token = security.create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
