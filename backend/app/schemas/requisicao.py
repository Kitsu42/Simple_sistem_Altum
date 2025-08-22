from pydantic import BaseModel
from datetime import datetime
from app.models.requisicao import StatusRC

class RCBase(BaseModel):
    rc_numero: str
    ns_numero: str | None = None
    empresa_id: int
    filial_id: int
    solicitante: str | None = None
    observacoes: str | None = None
    status: StatusRC = StatusRC.nova

class RCCreate(RCBase):
    pass

class RCUpdate(BaseModel):
    ns_numero: str | None = None
    observacoes: str | None = None
    status: StatusRC | None = None

class RCOut(RCBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
