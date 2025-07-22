project_root/
│
├── main.py                  # Ponto de entrada principal
├── config.py                # Configurações globais (DB, paths, etc.)
├── requirements.txt         # Dependências
│
├── database/                # Tudo relacionado ao banco de dados
│   ├── __init__.py
│   ├── models.py            # Classes/entidades SQLAlchemy
│   ├── banco.py             # Conexão e inicialização
│   ├── seed.py              # Dados iniciais
│   └── migrations/          # Futuro: scripts Alembic
│
├── data_handlers/           # Entrada/saída de dados (Excel, relatórios)
│   ├── __init__.py
│   ├── excel_parser.py      # Leitura e parsing de planilhas
│   ├── report_generator.py  # Geração de relatórios (PDF/Excel)
│   └── exporters/           # Exportações específicas
│
├── views/                   # Telas e lógica de interface
│   ├── __init__.py
│   ├── common/              # Telas compartilhadas (login, dashboard)
│   │   ├── login_view.py
│   │   └── dashboard.py
│   ├── comprador/           # Telas específicas do comprador
│   │   ├── backlog.py
│   │   ├── cotacao.py
│   │   └── historico.py
│   └── admin/               # Telas específicas do admin
│       ├── painel_admin.py
│       ├── gestao_rc.py
│       └── relatorios.py
│
├── services/                # Lógica de negócio e regras do sistema
│   ├── __init__.py
│   ├── rc_service.py        # Controle de RC (status, atribuições)
│   ├── auth_service.py      # Controle de autenticação
│   ├── notification_service.py  # Alertas/Admin
│   └── logs_service.py      # Log de ações
│
└── utils/                   # Funções auxiliares
    ├── __init__.py
    ├── constants.py         # Constantes globais
    ├── formatters.py        # Funções de formatação
    └── helpers.py           # Funções utilitárias genéricas