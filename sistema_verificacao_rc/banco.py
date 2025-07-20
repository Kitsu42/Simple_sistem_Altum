from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from base import Base
from models import Usuario, Empresa, Filial, Requisicao

engine = create_engine(\"sqlite:///banco.db\", connect_args={\"check_same_thread\": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---- Dados seed ----
EMPRESAS_SEED = [
    {
        \"codigo\": \"5SS\",
        \"nome\": \"5 ESTRELAS SPECIAL NORTE NORDESTE SERVICOS DE LIMPEZA LTDA\",
        \"filiais\": [
            (\"5SS-1\", \"11312620000182\", \"Aparecida\"),
            (\"5SS-2\", \"11312620000263\", \"Recife\"),
            (\"5SS-3\", \"11312620000344\", \"Fortaleza\"),
            (\"5SS-4\", \"11312620000425\", \"Manaus\"),
            (\"5SS-5\", \"11312620000506\", \"Salvador\"),
            (\"5SS-6\", \"11312620000697\", \"São Paulo\"),
            (\"5SS-7\", \"11312620000778\", \"Belo Horizonte\"),
        ],
    },
    {
        \"codigo\": \"FIEL/TOTAL\",
        \"nome\": \"FIEL VIGILANCIA LTDA/TOTAL ADMINISTRACAO\",
        \"filiais\": [
            (\"FIEL-1A\", \"06088000000171\", \"Aparecida\"),
            (\"FIEL-1B\", \"01775654000150\", \"Aparecida de Goiânia\"),
            (\"FIEL-2\",  \"06088000000686\", \"Manaus\"),
            (\"FIEL-3\",  \"01775654000664\", \"Porto Velho\"),
            (\"FIEL-4\",  \"06088000000503\", \"Campo Grande\"),
            (\"FIEL-5\",  \"06088000000414\", \"Cuiabá\"),
            (\"FIEL-7\",  \"06088000000252\", \"Palmas\"),
        ],
    },
    {
        \"codigo\": \"TS/TG\",
        \"nome\": \"TECNOSEG/TECNOGUARDA VIGILANCIA E SEGURANCA LTDA\",
        \"filiais\": [
            (\"TS-1\", \"02361081000180\", \"Goiânia\"),
            (\"TS-2\", \"02361081000261\", \"Cuiabá\"),
            (\"TS-3\", \"03277956000204\", \"Cuiabá\"),
        ],
    },
]


def _limpa_cnpj(cnpj: str) -> str:
    return \"\".join(ch for ch in str(cnpj) if ch.isdigit())


def popular_empresas_filiais(session):
    if session.query(Empresa).count() > 0:
        return
    for emp in EMPRESAS_SEED:
        e = Empresa(codigo=emp[\"codigo\"], nome=emp[\"nome\"])
        session.add(e)
        session.flush()  # garante e.id
        for codigo, cnpj, cidade in emp[\"filiais\"]:
            f = Filial(
                empresa_id=e.id,
                codigo=codigo,
                cnpj=_limpa_cnpj(cnpj),
                cidade=cidade,
                nome_exibicao=f\"{codigo} - {cidade}\",
            )
            session.add(f)
    session.commit()


def popular_usuarios_iniciais(session):
    if session.query(Usuario).count() == 0:
        session.add_all([
            Usuario(nome=\"admin\", senha=\"admin123\", cargo=\"admin\"),
            Usuario(nome=\"user01\", senha=\"user01\", cargo=\"comprador\"),
        ])
        session.commit()


def _ensure_filial_column(engine):
    \"\"\"Garante que a coluna filial_id exista em 'requisicoes' (SQLite).\"\"\"
    with engine.connect() as conn:
        cols = [row[1] for row in conn.execute(text(\"PRAGMA table_info(requisicoes)\"))]
        if \"filial_id\" not in cols:
            conn.execute(text(\"ALTER TABLE requisicoes ADD COLUMN filial_id INTEGER\"))
            # FK não é aplicada retroativamente em SQLite via ALTER, mas ok para nossa transição.


def migrar_requisicoes_filial(session):
    \"\"\"Tenta vincular requisições existentes a filiais seed com heurísticas simples.\"\"\"
    filiais = session.query(Filial).all()

    def match(emp_txt, fil_txt):
        t_emp = (emp_txt or \"\").lower()
        t_fil = (fil_txt or \"\").lower()
        for f in filiais:
            if f.codigo and f.codigo.lower() in t_emp:
                return f
            if f.codigo and f.codigo.lower() in t_fil:
                return f
            if f.cidade and f.cidade.lower() in t_fil:
                return f
            if f.empresa and f.empresa.codigo and f.empresa.codigo.lower() in t_emp:
                return f
        return None

    recs = session.query(Requisicao).filter(Requisicao.filial_id.is_(None)).all()
    changed = 0
    for r in recs:
        f = match(r.empresa_txt, r.filial_txt)
        if f:
            r.filial_id = f.id
            changed += 1
    if changed:
        session.commit()
        print(f\"[MIGRAÇÃO] Vinculadas {changed} requisições a filiais.\")


def criar_banco():
    print(\"👉 Criando/atualizando banco...\")
    Base.metadata.create_all(bind=engine)
    _ensure_filial_column(engine)
    session = SessionLocal()
    try:
        popular_empresas_filiais(session)
        popular_usuarios_iniciais(session)
        migrar_requisicoes_filial(session)
    finally:
        session.close()
    print(\"✅ Banco pronto.\")