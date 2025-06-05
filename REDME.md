# CRUD de Tarefas com Flask

Este é um aplicativo web simples de Gerenciamento de Tarefas (CRUD - Create, Read, Update, Delete) desenvolvido com o framework Flask em Python.

## Funcionalidades

* **Adicionar Tarefas:** Crie novas tarefas com uma descrição.
* **Listar Tarefas:** Visualize todas as tarefas existentes, ordenadas da mais recente para a mais antiga.
* **Atualizar Tarefas:** Edite a descrição de uma tarefa existente.
* **Excluir Tarefas:** Remova tarefas da lista.
* **Registro de Data e Hora:** Cada tarefa exibe a data e hora em que foi criada (no fuso horário de Brasília/São Paulo).
* **Mensagens de Feedback:** Notificações na tela para ações de sucesso ou erros.

## Tecnologias Utilizadas

* **Backend:**
    * Python
    * Flask
    * Flask-SQLAlchemy (para interação com o banco de dados SQLite)
    * WTForms e Flask-WTF (para formulários e validação, embora o formulário de registro seja um exemplo extra)
    * `pytz` (para manipulação de fuso horário)
* **Banco de Dados:** SQLite (banco de dados padrão `site.db`)
* **Frontend:**
    * HTML
    * CSS (estilização básica personalizada)

## Como Rodar o Projeto Localmente

Siga estes passos para configurar e executar o aplicativo em sua máquina:

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
    * **Windows (PowerShell):**
        ```bash
        .\venv\Scripts\activate
        ```
    * **Linux/macOS (Bash/Zsh):**
        ```bash
        source venv/bin/activate
        ```

3.  **Instale as Dependências:**
    Com o ambiente virtual ativado, instale as bibliotecas necessárias:
    ```bash
    pip install Flask Flask-SQLAlchemy Flask-WTF pytz
    ```
    (Você pode gerar um `requirements.txt` com `pip freeze > requirements.txt` para futuras instalações mais fáceis).

4.  **Execute o Aplicativo:**
    ```bash
    python app.py
    ```

5.  **Acesse no Navegador:**
    Abra seu navegador e acesse: `http://127.0.0.1:5153/`

### Observação Importante sobre o Banco de Dados

* Este projeto utiliza SQLite (`site.db`).
* Se você adicionar ou remover colunas no modelo `Tasks` (`app.py`), o banco de dados existente (`site.db`) **não será atualizado automaticamente**. Para que as mudanças no esquema do banco de dados entrem em vigor:
    1.  Pare o servidor Flask (Ctrl+C).
    2.  **Delete o arquivo `site.db`** (e a pasta `instance` se ela existir na raiz do projeto).
    3.  Execute `python app.py` novamente. O `db.create_all()` irá recriar o banco com o esquema atualizado.

## Melhorias Futuras Possíveis

* Autenticação e Registro de Usuários.
* Paginação para listas longas de tarefas.
* Filtros e busca por tarefas.
* Marcação de tarefas como "concluídas".
* Interface mais responsiva com um framework CSS (ex: Bootstrap).

## Autor

* [Lucas Gabriel]