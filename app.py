from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField # Importe SelectField
from wtforms.validators import DataRequired, InputRequired, Email, EqualTo, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime
import pytz # Para fusos horários

app = Flask(__name__)

# --- Configurações do Aplicativo ---
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --------------------------------------------------------------------------------------------------
# FUSO HORÁRIO E FILTRO JINJA PERSONALIZADO
# --------------------------------------------------------------------------------------------------

# Definindo o fuso horário de Brasília/São Paulo
BRAZIL_TIMEZONE = pytz.timezone('America/Sao_Paulo')

# Filtro Jinja para converter a data/hora de UTC para o fuso horário especificado
@app.template_filter('localdatetime')
def format_local_datetime(utc_dt):
    if utc_dt is None:
        return ""
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(BRAZIL_TIMEZONE)
    return local_dt.strftime('%d/%m/%Y às %H:%M:%S')

# --------------------------------------------------------------------------------------------------
# MODELOS DO BANCO DE DADOS
# --------------------------------------------------------------------------------------------------

# Modelo de Usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Modelo de Tarefa
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    # NOVO CAMPO: priority (Alta, Média, Baixa)
    priority = db.Column(db.String(10), nullable=False, default='Média') # Default para 'Média'

    def __repr__(self):
        return f"Task('{self.description}', Completed: {self.completed}, Priority: {self.priority})"

# --------------------------------------------------------------------------------------------------
# FORMULÁRIOS WTFORMS
# --------------------------------------------------------------------------------------------------

# Formulário de Registro de Usuário (mantido igual)
class RegisterForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), InputRequired(), EqualTo('confirm', message='As senhas devem ser iguais.')])
    confirm = PasswordField('Confirme a Senha', validators=[DataRequired()])
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está registrado.')

# Formulário de Login de Usuário (mantido igual)
class LoginForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

# --------------------------------------------------------------------------------------------------
# DECORADORES PERSONALIZADOS
# --------------------------------------------------------------------------------------------------

# Decorador para exigir login (mantido igual)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# --------------------------------------------------------------------------------------------------
# ROTAS DA APLICAÇÃO
# --------------------------------------------------------------------------------------------------

# Rota da página inicial - ONDE AS TAREFAS SÃO EXIBIDAS, FILTRADAS E PAGINADAS
@app.route('/')
def index():
    # Parâmetros de Filtro e Busca
    search_query = request.args.get('search_query', '')
    status_filter = request.args.get('status_filter', 'all')
    priority_filter = request.args.get('priority_filter', 'all')
    page = request.args.get('page', 1, type=int) # Página atual para paginação
    per_page = 5 # Número de itens por página (ajuste conforme necessário)

    # Inicia a consulta
    query = Task.query

    # Aplica filtro de status
    if status_filter == 'completed':
        query = query.filter_by(completed=True)
    elif status_filter == 'pending':
        query = query.filter_by(completed=False)

    # Aplica filtro de prioridade
    if priority_filter != 'all':
        query = query.filter_by(priority=priority_filter)

    # Aplica busca textual (case-insensitive)
    if search_query:
        query = query.filter(Task.description.ilike(f'%{search_query}%'))

    # Ordena as tarefas
    # Ordem de prioridade (Alta, Média, Baixa) e depois por data de criação
    if priority_filter == 'all': # Só ordena por prioridade se não estiver filtrando uma prioridade específica
        # Usando a lógica de ordem para strings
        query = query.order_by(
            db.case(
                (Task.priority == 'Alta', 1),
                (Task.priority == 'Média', 2),
                (Task.priority == 'Baixa', 3),
                else_=4 # Para qualquer outra prioridade inesperada
            ),
            Task.created_at.desc() # Depois ordena pela data de criação
        )
    else:
        query = query.order_by(Task.created_at.desc()) # Se já está filtrando, só ordena por data

    # Aplica paginação
    tasks_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    tasks = tasks_pagination.items # Obtém as tarefas da página atual

    return render_template('index.html',
                           tasks=tasks,
                           tasks_pagination=tasks_pagination, # Passa o objeto de paginação para o template
                           current_filter_status=status_filter,
                           current_filter_priority=priority_filter,
                           current_search_query=search_query)


# Rota para criar uma nova tarefa
@app.route('/create_task', methods=['POST'])
@login_required
def create_task():
    description = request.form.get('description')
    priority = request.form.get('priority', 'Média') # Pega a prioridade do formulário, default Média
    
    if not description:
        flash('A descrição da tarefa não pode estar vazia.', 'error')
        return redirect(url_for('index'))

    new_task = Task(description=description, priority=priority) # Inclui a prioridade
    db.session.add(new_task)
    db.session.commit()
    flash('Tarefa criada com sucesso!', 'success')
    return redirect(url_for('index'))

# Rota para deletar uma tarefa (mantido igual)
@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Tarefa excluída com sucesso!', 'info')
    return redirect(url_for('index'))

# Rota para atualizar uma tarefa
@app.route('/update_task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    new_description = request.form.get('description')
    new_priority = request.form.get('priority') # Pega a nova prioridade do formulário

    if not new_description:
        flash('A descrição da tarefa não pode estar vazia.', 'error')
        return redirect(url_for('index'))
    
    task.description = new_description
    if new_priority in ['Alta', 'Média', 'Baixa']: # Valida a prioridade recebida
        task.priority = new_priority
        
    db.session.commit()
    flash('Tarefa atualizada com sucesso!', 'success')
    return redirect(url_for('index'))

# Rota para alternar o status de conclusão da tarefa (mantido igual)
@app.route('/complete_task/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    if task.completed:
        flash('Tarefa marcada como concluída!', 'success')
    else:
        flash('Tarefa marcada como pendente novamente.', 'info')
    return redirect(url_for('index'))

# Rota de Registro de Usuário (mantido igual)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        flash('Você já está logado.', 'info')
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Sua conta foi criada com sucesso! Agora você pode fazer login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Rota de Login de Usuário (mantido igual)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        flash('Você já está logado.', 'info')
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            flash('Login bem-sucedido!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Login inválido. Verifique seu nome de usuário e senha.', 'error')
    return render_template('login.html', form=form)

# Rota de Logout de Usuário (mantido igual)
@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

# --------------------------------------------------------------------------------------------------
# INICIALIZAÇÃO DA APLICAÇÃO
# --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    with app.app_context():
        # ATENÇÃO: Ao adicionar a coluna 'priority' ao modelo Task,
        # VOCÊ PRECISA DELETAR o arquivo 'site.db'
        # e reiniciar o servidor para que o banco de dados seja recriado com a nova coluna.
        db.create_all()
    app.run(debug=True, port=5153)