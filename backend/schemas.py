from pydantic import BaseModel
from datetime import datetime

class PurchaseRequestBase(BaseModel):
    requester_name: str
    description: str
    status: str

class PurchaseRequestCreate(PurchaseRequestBase):
    pass

class PurchaseRequest(PurchaseRequestBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
