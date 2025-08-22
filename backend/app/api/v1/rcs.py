from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_current_user
from app.schemas.requisicao import RCCreate, RCOut, RCUpdate
from app.models.requisicao import StatusRC
from app.crud.rcs import create_rc, list_rcs, update_rc

router = APIRouter()

@router.get("/", response_model=list[RCOut])
def get_rcs(
    status: StatusRC | None = Query(default=None),
    db: Session = Depends(get_db),
    _ = Depends(get_current_user),
):
    return list_rcs(db, status)

@router.post("/", response_model=RCOut, status_code=201)
def post_rc(payload: RCCreate, db: Session = Depends(get_db), _ = Depends(get_current_user)):
    return create_rc(db, payload)

@router.patch("/{rc_id}", response_model=RCOut)
def patch_rc(rc_id: int, payload: RCUpdate, db: Session = Depends(get_db), _ = Depends(get_current_user)):
    rc = update_rc(db, rc_id, payload)
    if not rc:
        raise HTTPException(status_code=404, detail="RC não encontrada")
    return rc
