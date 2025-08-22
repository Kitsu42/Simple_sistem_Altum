from sqlalchemy.orm import Session
from app.models.requisicao import Requisicao, StatusRC
from app.schemas.requisicao import RCCreate, RCUpdate

def create_rc(db: Session, data: RCCreate) -> Requisicao:
    rc = Requisicao(**data.model_dump())
    db.add(rc)
    db.commit()
    db.refresh(rc)
    return rc

def list_rcs(db: Session, status: StatusRC | None = None) -> list[Requisicao]:
    q = db.query(Requisicao)
    if status:
        q = q.filter(Requisicao.status == status)
    return q.order_by(Requisicao.created_at.desc()).all()

def update_rc(db: Session, rc_id: int, data: RCUpdate) -> Requisicao | None:
    rc = db.get(Requisicao, rc_id)
    if not rc:
        return None
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(rc, k, v)
    db.commit()
    db.refresh(rc)
    return rc
