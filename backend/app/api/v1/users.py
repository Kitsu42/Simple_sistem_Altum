from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_current_user
from app.schemas.user import UserOut
from app.crud.users import list_users

router = APIRouter()

@router.get("/", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return list_users(db)

@router.get("/me", response_model=UserOut)
def get_me(current_user = Depends(get_current_user)):
    return current_user
