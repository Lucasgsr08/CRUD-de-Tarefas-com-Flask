# Projeto de Gerenciamento de Tarefas (CRUD)

Este projeto é uma aplicação web simples para gerenciamento de tarefas (CRUD - Create, Read, Update, Delete) desenvolvida com Flask e SQLAlchemy. Ele permite aos usuários adicionar, visualizar, editar e excluir tarefas, além de oferecer funcionalidades de busca e filtragem.

## Alterações Recentes na Interface (UI/UX)

Foram implementadas melhorias significativas na interface do usuário para otimizar a experiência e a usabilidade:

* **Visibilidade das Tarefas Concluídas:** Corrigido o problema onde o texto das tarefas concluídas ficava invisível. Agora, a descrição das tarefas prontas está claramente visível.
* **Edição de Tarefas via Modal:** A funcionalidade de edição de tarefas foi aprimorada. Em vez de campos de edição inline, agora utilizamos um modal (janela pop-up) para editar a descrição e a prioridade da tarefa, proporcionando uma interface mais limpa e intuitiva.
* **Alinhamento e Simetria dos Botões de Ação:** Os botões "EDITAR" e "EXCLUIR" na lista de tarefas foram alinhados para ficarem lado a lado, com o mesmo tamanho e sem bordas indesejadas, conferindo um aspecto mais simétrico e profissional à interface.

## Como Executar o Projeto

1.  **Clone o repositório:**
    ```bash
    git clone [SEU_LINK_DO_REPOSITORIO]
    cd [NOME_DA_PASTA_DO_PROJETO]
    ```
2.  **Crie e ative um ambiente virtual (opcional, mas recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Linux/macOS
    # ou
    venv\Scripts\activate     # No Windows
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    (Certifique-se de ter um arquivo `requirements.txt` com `Flask`, `SQLAlchemy`, etc.)
4.  **Execute a aplicação:**
    ```bash
    python app.py
    ```
    O aplicativo estará disponível em `http://127.0.0.1:5153/`.

## Funcionalidades Atuais

* **Criar Tarefa:** Adicionar novas tarefas com descrição e prioridade.
* **Listar Tarefas:** Visualizar todas as tarefas existentes.
* **Editar Tarefa:** Atualizar a descrição e/ou prioridade de uma tarefa através de um modal de edição.
* **Excluir Tarefa:** Remover tarefas da lista.
* **Marcar como Concluída:** Alternar o status de uma tarefa entre pendente e concluída.
* **Filtragem de Tarefas:** Filtrar tarefas por status (todas, pendentes, concluídas) e prioridade (Alta, Média, Baixa).
* **Busca de Tarefas:** Buscar tarefas por palavras-chave na descrição.
* **Paginação:** Navegar entre múltiplas páginas de tarefas para melhor gerenciamento.

## Próximas Funcionalidades (Sugestões para Aprimoramento)

Aqui estão algumas ideias para expandir e melhorar este projeto CRUD:

* **Autenticação e Autorização de Usuários:**
    * **Registro de Usuários:** Permitir que novos usuários se cadastrem.
    * **Login/Logout:** Funcionalidades de login e logout para gerenciar sessões de usuários.
    * **Tarefas por Usuário:** Associar tarefas a usuários específicos, para que cada usuário veja apenas suas próprias tarefas.
* **Datas de Vencimento:**
    * Adicionar um campo para `data de vencimento` para cada tarefa.
    * Permitir filtrar e ordenar tarefas por data de vencimento.
    * Notificações visuais para tarefas próximas do vencimento ou atrasadas.
* **Categorias/Tags para Tarefas:**
    * Permitir que os usuários atribuam categorias (ex: Trabalho, Pessoal, Estudos) ou tags a tarefas.
    * Funcionalidade de filtragem e busca por categorias/tags.
* **Ordenação de Tarefas:**
    * Opções de ordenação para a lista de tarefas (por prioridade, data de criação, data de vencimento, status).
* **Confirmação de Exclusão:**
    * Adicionar um pop-up de confirmação antes de excluir uma tarefa para evitar exclusões acidentais.
* **Validação de Formulários Aprimorada:**
    * Validação mais robusta no lado do cliente (JavaScript) e no lado do servidor para os campos dos formulários.
* **Melhorias na Interface do Usuário:**
    * **Drag-and-Drop:** Arrastar e soltar tarefas para reordená-las ou mudar de status.
    * **Modo Escuro:** Opção para alternar entre temas claro e escuro.
    * **Animações e Transições:** Adicionar pequenas animações para uma experiência mais fluida.
* **Recursos de Colaboração (Futuro):**
    * Permitir compartilhar tarefas ou listas de tarefas com outros usuários.

Este `README.md` será um documento vivo, atualizado à medida que o projeto evolui.