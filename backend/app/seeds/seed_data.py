"""
Executar com:
  uvicorn app.main:app --reload
ou popular manualmente:
  python -m app.seeds.seed_data
"""
from app.core.db import Base, engine, SessionLocal
from app.models.organization import Empresa, Filial
from app.crud.users import create_user, get_user_by_email
from app.models.user import UserRole
from app.models.requisicao import Requisicao, StatusRC

def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Empresas & Filiais
        acme = db.query(Empresa).filter_by(nome="ACME").first()
        if not acme:
            acme = Empresa(nome="ACME", cnpj="00.000.000/0001-00")
            db.add(acme); db.commit(); db.refresh(acme)
        filial_a = db.query(Filial).filter_by(nome="Matriz", empresa_id=acme.id).first()
        if not filial_a:
            filial_a = Filial(empresa_id=acme.id, nome="Matriz", cnpj="00.000.000/0001-01")
            db.add(filial_a); db.commit()

        # Usuários
        if not get_user_by_email(db, "admin@acme.com"):
            create_user(db, "Admin", "admin@acme.com", "admin123", UserRole.admin)
        if not get_user_by_email(db, "gestor@acme.com"):
            create_user(db, "Gestor", "gestor@acme.com", "gestor123", UserRole.gestor)
        if not get_user_by_email(db, "comprador@acme.com"):
            create_user(db, "Comprador", "comprador@acme.com", "comprador123", UserRole.comprador)

        # RC exemplo
        has_rc = db.query(Requisicao).first()
        if not has_rc:
            db.add(Requisicao(
                rc_numero="RC-0001", ns_numero="NS-1001",
                empresa_id=acme.id, filial_id=filial_a.id,
                solicitante="João", observacoes="Urgente",
                status=StatusRC.nova
            ))
            db.commit()
        print("Seed concluído.")
    finally:
        db.close()

if __name__ == "__main__":
    run()
