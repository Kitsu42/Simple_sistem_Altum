# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from backend.db import SessionLocal, init_db, PurchaseRequest
from backend import schemas
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import BytesIO

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Altere isso em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/purchase-request/", response_model=schemas.PurchaseRequest)
def create_request(request_data: schemas.PurchaseRequestCreate, db: Session = Depends(get_db)):
    pr = PurchaseRequest(
        requester_name=request_data.requester_name,
        description=request_data.description,
        status=request_data.status,
    )
    db.add(pr)
    db.commit()
    db.refresh(pr)
    return pr

@app.get("/purchase-request/", response_model=list[schemas.PurchaseRequest])
def list_requests(db: Session = Depends(get_db)):
    return db.query(PurchaseRequest).all()

@app.post("/upload-excel/")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))

        for _, row in df.iterrows():
            pr = PurchaseRequest(
                requester_name=row.get("requester_name", "Desconhecido"),
                description=row.get("description", ""),
                status=row.get("status", "Pendente")
            )
            db.add(pr)
        db.commit()
        return {"status": "success", "message": "Arquivo processado."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
