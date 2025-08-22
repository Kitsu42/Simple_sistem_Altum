frontend/
├── src/
│   ├── components/
│   │   └── PrivateRoute.tsx        # Protege rotas autenticadas
│   │
│   ├── pages/
│   │   ├── Login.tsx               # Tela de login
│   │   └── Dashboard.tsx           # Exemplo de rota protegida
│   │
│   ├── services/
│   │   └── authService.ts          # Requisições de login/logout
│   │
│   ├── routes/
│   │   └── router.tsx              # Definição de rotas públicas e privadas
│   │
│   ├── context/
│   │   └── AuthContext.tsx         # Contexto global de autenticação
│   │
│   ├── App.tsx                     # App principal
│   └── main.tsx                    # Ponto de entrada (ReactDOM)
│
├── index.html
├── package.json
└── tsconfig.json
└── vite.config.ts
└── .env

backend/
│── alembic/               # Migrations do banco (Alembic)
│── app/
│   ├── api/               # Rotas (separadas por domínio)
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py    # Rotas de autenticação
│   │       ├── users.py   # Rotas de usuários
│   │       └── rcs.py     # Rotas de requisições de compra
│   │
│   ├── core/              # Configurações centrais
│   │   ├── __init__.py
│   │   ├── config.py      # Variáveis de ambiente
│   │   ├── security.py    # JWT, hashing, permissões
│   │   └── db.py          # Conexão com banco (SQLAlchemy)
│   │
│   ├── crud/              # Operações de banco (repository layer)
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── rcs.py
│   │
│   ├── models/            # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── requisicao.py
│   │
│   ├── schemas/           # Pydantic (entrada/saída)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── requisicao.py
│   │
│   ├── services/          # Serviços extras (importação Excel, emails, etc.)
│   │   └── __init__.py
│   │
│   ├── seeds/             # Dados iniciais (usuários, empresas, etc.)
│   │   └── seed_data.py
│   │
│   └── main.py            # Ponto de entrada da API
│
├── .env                   # Variáveis de ambiente
├── alembic.ini            # Configuração do Alembic
├── requirements.txt       # Dependências
└── pyproject.toml         # (opcional, se usar poetry)
