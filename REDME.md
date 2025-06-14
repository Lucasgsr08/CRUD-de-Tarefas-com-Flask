# Task Master

Este é um projeto de gerenciamento de tarefas simples, desenvolvido com Flask, SQLAlchemy e Bootstrap. Ele permite que os usuários criem, visualizem, editem, excluam e filtrem suas tarefas.

## Funcionalidades Implementadas

Até o momento, as seguintes funcionalidades foram implementadas no projeto:

* **Autenticação de Usuários:**
    * Registro de novos usuários.
    * Login de usuários existentes.
    * Logout de usuários.
* **Gerenciamento de Tarefas (CRUD):**
    * **Criar:** Adicionar novas tarefas com descrição, prioridade, data de vencimento e categoria.
    * **Visualizar:** Exibir uma lista de todas as tarefas.
    * **Atualizar/Editar:** Modificar a descrição, prioridade, data de vencimento, categoria e status de uma tarefa existente.
    * **Excluir:** Remover tarefas.
* **Filtros e Busca:**
    * Filtrar tarefas por descrição, status, prioridade, data de vencimento e categoria.
    * Ordenação da lista de tarefas por diferentes critérios.
* **Paginação:**
    * Exibição de tarefas em páginas para melhor gerenciamento de grandes volumes de dados.
* **Feedback ao Usuário:**
    * Mensagens flash para informar sobre sucesso ou erro em operações (ex: "Tarefa criada com sucesso!").
* **Design Responsivo:**
    * Utilização do Bootstrap 5 para garantir uma interface que se adapta a diferentes tamanhos de tela.
* **Animações e Transições Básicas (CSS):**
    * Transições suaves de cores para elementos como cards e botões ao interagir com o tema, utilizando variáveis CSS.

## Modo Escuro (Estado Atual)

Uma tentativa de implementar um modo escuro puramente com HTML e CSS foi feita. Um botão de toggle está visível na interface. No entanto, **o modo escuro ainda não está funcionando**. O clique no botão não provoca nenhuma alteração visual na página.

**Causa Provável do Problema:**
Apesar do CSS (`dark_mode.css`) estar configurado corretamente com variáveis e transições, a interação entre o checkbox oculto e a tag `<body>` (usando o seletor `~ body`) é muito sensível à estrutura HTML. Se o checkbox não estiver posicionado como um irmão direto e anterior do `<body>`, o CSS não conseguirá aplicar as variáveis do tema escuro. A última tentativa de correção envolveu mover o checkbox para ser o primeiro elemento dentro do `<body>` no `layout.html`.

## Como Corrigir o Modo Escuro (Próximos Passos de Depuração)

1.  **Verifique a Posição do Checkbox no `templates/layout.html`:**
    * Certifique-se ABSOLUTAMENTE que o `<input type="checkbox" id="darkModeToggleCSS" class="d-none">` é o **primeiro elemento diretamente dentro da tag `<body>`**. Ele não deve estar dentro de `<nav>`, `<main>`, ou qualquer outra div.
    ```html
    <body>
        <input type="checkbox" id="darkModeToggleCSS" class="d-none"> 
        <nav class="navbar navbar-expand-lg ...">
            </nav>
        <main class="container ...">
            </main>
        </body>
    ```
2.  **Confirme o `dark_mode.css`:**
    * Verifique novamente se o conteúdo de `static/css/dark_mode.css` é exatamente o que foi fornecido nas últimas interações, com as variáveis `root` e o seletor `#darkModeToggleCSS:checked ~ body`.
3.  **Reinicie o Servidor Flask:**
    * Sempre reinicie o servidor (`python app.py`) após fazer alterações no código Python ou nos templates.
4.  **Limpe o Cache do Navegador:**
    * Ao testar no navegador, use `Ctrl + Shift + R` (ou `Ctrl + F5`) para fazer um recarregamento forçado da página e garantir que o navegador não esteja usando arquivos CSS antigos em cache.
5.  **Use as Ferramentas de Desenvolvedor (Inspecionar Elemento):**
    * Abra o site no navegador e pressione `F12`.
    * Vá para a aba "Elementos" (ou "Inspector").
    * Clique no botão "Modo Escuro / Modo Claro".
    * Inspecione a tag `<body>`. Na aba "Estilos" (Styles), veja se as variáveis CSS (`--bg-color`, `--text-color`, etc.) estão mudando. Se não mudarem, o seletor `#darkModeToggleCSS:checked ~ body` não está sendo aplicado.
    * Inspecione o `<input type="checkbox" id="darkModeToggleCSS">`. Tente marcá-lo/desmarcá-lo manualmente na aba de elementos. Se o tema mudar ao fazer isso, o problema é na associação do `label` com o `input`. Se não mudar, o problema é no seletor CSS principal.

## Possíveis Melhorias Futuras

Aqui estão algumas ideias para expandir e aprimorar o seu projeto no futuro:

### Backend (Python/Flask)

* **Persistência do Modo Escuro:** Implementar a persistência da preferência do modo escuro no banco de dados para cada usuário ou usando cookies (requer JavaScript e uma rota Flask para salvar a preferência).
* **Notificações de Vencimento:** Enviar notificações por e-mail ou no próprio aplicativo para tarefas que estão se aproximando da data de vencimento.
* **Permissões e Papéis:** Adicionar diferentes níveis de usuário (ex: administrador, usuário comum) com permissões distintas.
* **API RESTful:** Expor uma API para que outras aplicações possam interagir com as tarefas.
* **Busca Mais Avançada:** Implementar busca por palavras-chave em múltiplos campos, talvez com suporte a operadores lógicos.
* **Integração com Calendário:** Sincronizar datas de vencimento com serviços de calendário externos (Google Calendar, Outlook).
* **Validação de Formulários Mais Robusta:** Adicionar validações mais complexas no backend.

### Frontend (HTML/CSS)

* **Drag-and-Drop (Requer JavaScript):** Permitir que os usuários reorganizem a ordem das tarefas na lista arrastando e soltando. Isso exigiria JavaScript para a interface e uma atualização via Flask para salvar a nova ordem.
* **Animações e Transições Mais Complexas (Requer JavaScript para controle):**
    * Animações de entrada/saída para novos cards de tarefa ou ao filtrar.
    * Feedback visual mais dinâmico ao marcar/desmarcar tarefas.
* **Melhorias na UX/UI:**
    * Melhorar o design do formulário de adição/edição de tarefas.
    * Adicionar ícones para categorias ou status.
    * Personalização de cores para prioridades ou categorias pelo usuário.
* **Componentes Interativos:** Adicionar um seletor de data (date picker) mais amigável para a data de vencimento (geralmente feito com JavaScript).
* **Responsividade Aprimorada:** Otimizar o layout para dispositivos móveis específicos.

### Geral

* **Testes Automatizados:** Escrever testes de unidade e integração para o backend (Flask) e talvez testes end-to-end para o frontend.
* **Dockerização:** Empacotar a aplicação em um container Docker para facilitar o deployment.
* **Deployment:** Publicar a aplicação em um servidor web real (ex: Heroku, AWS, Google Cloud).
* **Documentação Adicional:** Detalhar a estrutura do projeto, dependências, e como configurar o ambiente de desenvolvimento.

Este README serve como um guia para o estado atual e o futuro potencial do seu projeto Task Master!