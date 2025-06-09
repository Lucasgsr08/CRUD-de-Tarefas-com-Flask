from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Email, EqualTo, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)

# --- Configurações do Aplicativo ---
# !!! MUDE ESTA CHAVE PARA UMA ÚNICA E COMPLEXA EM PRODUÇÃO !!!
app.config['SECRET_KEY'] = os.urandom(24).hex() # Gera uma chave aleatória de 24 bytes para desenvolvimento
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # Define o banco de dados SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Desativa o rastreamento de modificações (recomendado)

db = SQLAlchemy(app)

# --------------------------------------------------------------------------------------------------
# MODELOS DO BANCO DE DADOS
# --------------------------------------------------------------------------------------------------

# Modelo de Usuário para registro e login
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) # Armazena o hash da senha

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    # Método para gerar o hash da senha antes de salvar
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Método para verificar a senha fornecida com o hash salvo
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Modelo de Tarefa
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    # OPCIONAL: Para associar tarefas a usuários específicos
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # user = db.relationship('User', backref='tasks', lazy=True)

    def __repr__(self):
        return f"Task('{self.description}')"

# --------------------------------------------------------------------------------------------------
# FORMULÁRIOS WTFORMS
# --------------------------------------------------------------------------------------------------

# Formulário de Registro de Usuário
class RegisterForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), InputRequired(), EqualTo('confirm', message='As senhas devem ser iguais.')])
    confirm = PasswordField('Confirme a Senha', validators=[DataRequired()])
    submit = SubmitField('Registrar')

    # Validadores personalizados para verificar se o nome de usuário ou email já existem
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está registrado. Por favor, use outro.')

# Formulário de Login de Usuário
class LoginForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

# --------------------------------------------------------------------------------------------------
# DECORADORES PERSONALIZADOS
# --------------------------------------------------------------------------------------------------

# Decorador para exigir login em certas rotas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'error')
            return redirect(url_for('login', next=request.url)) # Redireciona para login e tenta voltar
        return f(*args, **kwargs)
    return decorated_function

# --------------------------------------------------------------------------------------------------
# ROTAS DA APLICAÇÃO
# --------------------------------------------------------------------------------------------------

# Rota da página inicial - ONDE AS TAREFAS SÃO EXIBIDAS
@app.route('/')
# @login_required # Remova o comentário para exigir login para acessar a página inicial
def index():
    # Isso é para depuração! Vai mostrar as tarefas no terminal do Flask
    # print("DEBUG: Entrou na rota index()")

    # Consulta todas as tarefas do banco de dados
    tasks = Task.query.all()

    # Se você implementou user_id para tarefas (descomente as linhas abaixo no modelo Task também):
    # if 'user_id' in session:
    #     tasks = Task.query.filter_by(user_id=session['user_id']).all()
    # else:
    #     tasks = [] # Se não estiver logado, não mostra tarefas

    # print(f"DEBUG: Tarefas recuperadas: {tasks}") # Imprime as tarefas recuperadas para depuração

    return render_template('index.html', tasks=tasks)

# Rota para criar uma nova tarefa
@app.route('/create_task', methods=['POST'])
@login_required # Exige login para criar tarefas
def create_task():
    description = request.form.get('description')
    if not description:
        flash('A descrição da tarefa não pode estar vazia.', 'error')
        return redirect(url_for('index'))

    new_task = Task(description=description)
    # Se você implementou user_id para tarefas:
    # if 'user_id' in session:
    #     new_task.user_id = session['user_id']

    db.session.add(new_task)
    db.session.commit() # ESSENCIAL: Garante que a tarefa é salva no DB
    flash('Tarefa criada com sucesso!', 'success')
    return redirect(url_for('index'))

# Rota para deletar uma tarefa
@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required # Exige login para deletar tarefas
def delete_task(task_id):
    task = Task.query.get_or_404(task_id) # Pega a tarefa ou retorna 404 se não existir

    # Opcional: Verificar se a tarefa pertence ao usuário logado antes de deletar
    # if 'user_id' in session and task.user_id != session['user_id']:
    #    flash('Você não tem permissão para deletar esta tarefa.', 'error')
    #    return redirect(url_for('index'))

    db.session.delete(task)
    db.session.commit() # ESSENCIAL: Garante que a deleção é salva no DB
    flash('Tarefa excluída com sucesso!', 'info')
    return redirect(url_for('index'))

# Rota para atualizar uma tarefa
@app.route('/update_task/<int:task_id>', methods=['POST'])
@login_required # Exige login para atualizar tarefas
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    new_description = request.form.get('description')

    if not new_description:
        flash('A descrição da tarefa não pode estar vazia.', 'error')
        return redirect(url_for('index'))

    # Opcional: Verificar se a tarefa pertence ao usuário logado antes de atualizar
    # if 'user_id' in session and task.user_id != session['user_id']:
    #    flash('Você não tem permissão para atualizar esta tarefa.', 'error')
    #    return redirect(url_for('index'))

    task.description = new_description
    db.session.commit() # ESSENCIAL: Garante que a atualização é salva no DB
    flash('Tarefa atualizada com sucesso!', 'success')
    return redirect(url_for('index'))

# Rota de Registro de Usuário
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session: # Redireciona se o usuário já estiver logado
        flash('Você já está logado.', 'info')
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit() # ESSENCIAL: Garante que o novo usuário é salvo no DB
        flash('Sua conta foi criada com sucesso! Agora você pode fazer login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Rota de Login de Usuário
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session: # Redireciona se o usuário já estiver logado
        flash('Você já está logado.', 'info')
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id # Armazena o ID do usuário na sessão
            flash('Login bem-sucedido!', 'success')
            next_page = request.args.get('next') # Tenta retornar para a página anterior
            return redirect(next_page or url_for('index'))
        else:
            flash('Login inválido. Verifique seu nome de usuário e senha.', 'error')
    return render_template('login.html', form=form)

# Rota de Logout de Usuário
@app.route('/logout')
@login_required # Apenas usuários logados podem fazer logout
def logout():
    session.pop('user_id', None) # Remove o ID do usuário da sessão
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

# --------------------------------------------------------------------------------------------------
# INICIALIZAÇÃO DA APLICAÇÃO
# --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    with app.app_context():
        # ISSO É EXECUTADO APENAS UMA VEZ NA PRIMEIRA EXECUÇÃO.
        # Ele cria as tabelas User e Task se elas não existirem no site.db.
        # Se você alterar os modelos (adicionar/remover colunas), você DEVE:
        # 1. Parar o servidor Flask.
        # 2. DELETAR o arquivo 'site.db' na sua pasta de projeto.
        # 3. Reiniciar o servidor Flask.
        db.create_all()
    app.run(debug=True, port=5153) # Inicia o servidor Flask em modo de depuração na porta 5153