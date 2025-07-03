# Simple_sistem_Altum


# Sistema de verificação de RC
Funções esperadas:

    [ ] - adcionar tela de login separado.
    [X] - Ler as planilhas do backlog.
    [X] - Separar as requisições.
    [X] - Mostrar cada requisição como um card que deve apresentar n° de SC, quantidade de linhas, data de criação da SC e a quanto tempo está aberta.
    [ ] - Imprimir relatorios do estado de cada SC e guardar um historico.
    [X] - Adicionar quem está cuidando de cada RC.
    [X] - Adicionar sistema de login
    [ ] - Adicionar sistema de cotação
    [X] - Adicionar paginas de cotação, em espera e concluidas
    [ ] - Gerar sistema de prazo para cotações e gerar oc
    [X] - Organizar por filial e empresa
    [ ] - Tornar obrigatorio declarar o N° de OC para concluir a RC
    [ ] - Adcionar possibilidade de filtro que não atualize para todos ao mesmo tempo
    [ ] - Pagina de cotação deve conter
        [ ] - Lembrete de anexar NF
        [ ] - Lembrete de cobra fornecedor
        [ ] - Lembrete de enviar OC para o fornecedor
        [ ] - Informações do fornecedor (nome; numero; empresa)

Futuras funções:

    [ ] - Conseguir acessar o painel.
    [ ] - Verificar filial e retornar RCs com filial errada.
    [ ] - Aba de RCs em cotação.
    [ ] - Exibir o estado em que a RC está no painel.
    [ ] - Puchar o backlog direto do Senior

Extrutura:

        sistema_verificacao_rc/
    │
    ├── main.py                      # Entrada principal (controla rotas e sessão)
    ├── banco.py                     # Configuração do SQLAlchemy
    ├── base.py                      # Declarative Base do SQLAlchemy
    ├── models.py                    # Modelos de dados (ORM)
    ├── planilhas.py                 # Manipulação e leitura de planilhas Excel
    ├── utils.py                     # Funções auxiliares (ex: datas, conversões)
    ├── requirements.txt             # Dependências do projeto
    ├── README.md                    # Documentação básica
    │
    ├── auth/                        
    │   └── login.py                 # Lógica de autenticação e hash/token
    │
    ├── data/
    │   └── uploads/                 # Planilhas ou arquivos XML enviados
    │
    ├── reports/
    │   ├── gerar_pdf.py             # Função de gerar relatórios em PDF
    │   ├── gerar_xml.py             # Função de gerar relatórios em XML
    │
    └── views/
        ├── __init__.py              # Necessário para importar como pacote
        ├── acesso.py                # Página de login (exibe formulário de login)
        ├── backlog.py               # RCs recebidas (Backlog)
        ├── cotacao.py               # RCs em cotação
        ├── finalizado.py            # RCs finalizadas
        ├── analise.py               # OCs aguardando aprovação
        ├── erros.py                 # OCs com erro (XML externo)
        └── admin.py                 # Página exclusiva de administração
