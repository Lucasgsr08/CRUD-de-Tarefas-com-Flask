# Gerenciador de Tarefas com Autenticação de Usuários (Flask)

Este é um aplicativo web completo para gerenciamento de tarefas (CRUD - Create, Read, Update, Delete) com funcionalidades de autenticação de usuários. Desenvolvido com o framework Flask em Python, ele permite que usuários se registrem, façam login e gerenciem suas próprias tarefas de forma segura.

## Funcionalidades Principais

* **Autenticação de Usuários:**
    * **Registro de Conta:** Novos usuários podem criar suas contas com nome de usuário, e-mail e senha.
    * **Login Seguro:** Usuários registrados podem fazer login para acessar suas funcionalidades.
    * **Logout:** Funcionalidade para desconectar o usuário da sessão.
    * **Gerenciamento de Sessão:** Mantém o estado de login do usuário, protegendo rotas que exigem autenticação.

* **CRUD de Tarefas:**
    * **Adicionar Tarefas:** Crie novas tarefas com uma descrição.
    * **Listar Tarefas:** Visualize todas as tarefas existentes.
    * **Atualizar Tarefas:** Edite a descrição de uma tarefa existente.
    * **Excluir Tarefas:** Remova tarefas da lista.

* **Recursos Adicionais:**
    * **Mensagens de Feedback:** Notificações na tela (flash messages) para ações de sucesso, erros ou informações importantes (ex: "Tarefa criada com sucesso!", "Login inválido.").
    * **Layout Responsivo:** Utilização do Bootstrap para uma interface de usuário moderna e adaptável.

## Tecnologias Utilizadas

* **Backend:**
    * Python 3.x
    * **Flask:** Micro-framework web.
    * **Flask-SQLAlchemy:** Extensão para integrar SQLAlchemy (ORM) com Flask, facilitando a interação com o banco de dados.
    * **Flask-WTF & WTForms:** Para criar e validar formulários web de forma segura (incluindo proteção CSRF).
    * **Werkzeug.security:** Para hashing e verificação segura de senhas (criptografia bcrypt).
    * **email_validator:** Para validação de formato de e-mail nos formulários.

* **Banco de Dados:**
    * **SQLite:** Banco de dados leve e baseado em arquivo (`site.db`), ideal para desenvolvimento e pequenas aplicações.

* **Frontend:**
    * **HTML5:** Estrutura das páginas web.
    * **CSS:** Estilização personalizada.
    * **Bootstrap 5:** Framework CSS para componentes e responsividade da interface.

## Como Rodar o Projeto Localmente

Siga estes passos para configurar e executar o aplicativo em sua máquina.

1.  **Clone o Repositório:**
    ```bash
    git clone [LINK_DO_SEU_REPOSITORIO_AQUI]
    cd [NOME_DA_SUA_PASTA_DO_PROJETO]
    ```

2.  **Crie e Ative um Ambiente Virtual:**
    É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.
    ```bash
    python -m venv venv
    ```
    * **Windows (Command Prompt):**
        ```bash
        .\venv\Scripts\activate
        ```
    * **Windows (PowerShell):**
        ```bash
        .\venv\Scripts\Activate.ps1
        ```
    * **Linux/macOS (Bash/Zsh):**
        ```bash
        source venv/bin/activate
        ```

3.  **Instale as Dependências:**
    Com o ambiente virtual ativado, instale todas as bibliotecas necessárias:
    ```bash
    pip install Flask Flask-SQLAlchemy Flask-WTF Werkzeug email_validator
    ```
    *(Opcional: Você pode gerar um `requirements.txt` com `pip freeze > requirements.txt` para futuras instalações mais fáceis usando `pip install -r requirements.txt`).*

4.  **Execute o Aplicativo:**
    ```bash
    python app.py
    ```

5.  **Acesse no Navegador:**
    Abra seu navegador e acesse: `http://127.0.0.1:5153/`

### Observação Importante sobre o Banco de Dados

* Este projeto utiliza SQLite (`site.db`).
* Se você adicionar ou remover colunas em seus modelos (`User` ou `Task` no `app.py`), o banco de dados existente (`site.db`) **não será atualizado automaticamente** pelo Flask-SQLAlchemy. Para que as mudanças no esquema do banco de dados entrem em vigor:
    1.  Pare o servidor Flask (pressione `Ctrl+C` no terminal).
    2.  **Delete o arquivo `site.db`** (e qualquer arquivo `site.db-journal` se ele existir na raiz do projeto).
    3.  Execute `python app.py` novamente. O `db.create_all()` irá recriar o banco com o esquema atualizado, mas **você perderá todos os dados existentes**.

## Melhorias Futuras Possíveis

* **Associação de Tarefas a Usuários:** Permitir que cada usuário veja e gerencie apenas suas próprias tarefas.
* **Status da Tarefa:** Adicionar um campo para marcar tarefas como "Concluída" e permitir filtrar por status.
* **Data de Criação e Prazo:** Adicionar campos para datas de criação e prazos para as tarefas.
* **Prioridade da Tarefa:** Campo para definir a prioridade (ex: Alta, Média, Baixa).
* **Barra de Busca e Filtros:** Implementar funcionalidades de busca e filtragem de tarefas na interface.
* **Paginação:** Para lidar com um grande volume de tarefas.
* **Perfis de Usuário:** Uma página para o usuário visualizar e talvez editar suas informações de perfil.
* **Testes Automatizados:** Escrever testes de unidade e integração para garantir a funcionalidade.

## Autor

* [Lucas Gabriel]