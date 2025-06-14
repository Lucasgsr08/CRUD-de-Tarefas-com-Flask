from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate # Manter se você decidir usar Flask-Migrate

# Configuração do aplicativo Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui' # Mude para uma chave secreta forte e única

db = SQLAlchemy(app)
migrate = Migrate(app, db) # Manter se você decidir usar Flask-Migrate

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Modelos do Banco de Dados ---

# Modelo de Usuário
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    tasks = db.relationship('Task', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# Função para carregar o usuário pelo ID (necessário para o Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Modelo de Tarefa (MODIFICADO para incluir category)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    priority = db.Column(db.String(50), default='Média') # 'Baixa', 'Média', 'Alta'
    due_date = db.Column(db.Date, nullable=True)
    category = db.Column(db.String(100), nullable=True) # NOVO: Campo para categoria
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Task {self.id}: {self.description}>'

# Criação do banco de dados (se não existir) - REMOVA/COMENTE SE ESTIVER USANDO FLASK-MIGRATE
# with app.app_context():
#     db.create_all()

# --- Rotas da Aplicação ---

# Rota de Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not email or not password or not confirm_password:
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('register.html')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Nome de usuário já existe. Escolha outro.', 'danger')
            return render_template('register.html')

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Este email já está registrado. Use outro.', 'danger')
            return render_template('register.html')

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Nome de usuário ou senha inválidos.', 'danger')
    return render_template('login.html')

# Rota de Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

# Rota principal (MODIFICADA para filtros de categoria)
@app.route('/', methods=['GET'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search_query', '')
    status_filter = request.args.get('status_filter', 'all')
    priority_filter = request.args.get('priority_filter', 'all')
    due_date_filter = request.args.get('due_date_filter', 'all')
    category_filter = request.args.get('category_filter', 'all') # NOVO: Filtro de categoria
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')

    tasks_query = Task.query.filter_by(user_id=current_user.id)

    if search_query:
        tasks_query = tasks_query.filter(Task.description.contains(search_query))

    if status_filter == 'pending':
        tasks_query = tasks_query.filter_by(completed=False)
    elif status_filter == 'completed':
        tasks_query = tasks_query.filter_by(completed=True)

    if priority_filter != 'all':
        tasks_query = tasks_query.filter_by(priority=priority_filter)

    # Lógica do Filtro por Data de Vencimento
    today = date.today()
    if due_date_filter == 'today':
        tasks_query = tasks_query.filter_by(due_date=today)
    elif due_date_filter == 'upcoming':
        # Próximos 7 dias (incluindo hoje, se não estiver atrasada e não concluída)
        tasks_query = tasks_query.filter(
            Task.due_date >= today,
            Task.due_date <= (today + timedelta(days=7)),
            Task.completed == False
        )
    elif due_date_filter == 'overdue':
        tasks_query = tasks_query.filter(
            Task.due_date < today,
            Task.completed == False
        )
    
    # NOVO: Lógica do Filtro por Categoria
    if category_filter != 'all':
        tasks_query = tasks_query.filter(db.func.lower(Task.category) == db.func.lower(category_filter)) # Busca insensível a maiúsculas/minúsculas
    elif category_filter == 'none': # Para filtrar tarefas sem categoria
        tasks_query = tasks_query.filter(Task.category.is_(None))


    # Lógica de Ordenação
    if sort_by == 'created_at':
        if order == 'asc':
            tasks_query = tasks_query.order_by(Task.created_at.asc())
        else:
            tasks_query = tasks_query.order_by(Task.created_at.desc())
    elif sort_by == 'due_date':
        if order == 'asc':
            tasks_query = tasks_query.order_by(Task.due_date.asc().nulls_last()) 
        else:
            tasks_query = tasks_query.order_by(Task.due_date.desc().nulls_last())
    elif sort_by == 'priority':
        priority_order = {'Alta': 3, 'Média': 2, 'Baixa': 1}
        if order == 'asc':
             tasks_query = tasks_query.order_by(db.case(
                {p: value for p, value in priority_order.items()},
                value=Task.priority).asc())
        else:
            tasks_query = tasks_query.order_by(db.case(
                {p: value for p, value in priority_order.items()},
                value=Task.priority).desc())
    elif sort_by == 'status':
        if order == 'asc':
            tasks_query = tasks_query.order_by(Task.completed.asc())
        else:
            tasks_query = tasks_query.order_by(Task.completed.desc())


    tasks_pagination = tasks_query.paginate(
        page=page, per_page=5, error_out=False
    )
    tasks = tasks_pagination.items

    # Obter todas as categorias únicas para o filtro
    # Exclui categorias nulas e transforma em lista de strings únicas
    all_categories = db.session.query(Task.category).filter(
        Task.user_id == current_user.id, 
        Task.category.isnot(None)
    ).distinct().order_by(Task.category).all()
    all_categories = [c[0] for c in all_categories] # Extrai a string da tupla

    return render_template('index.html', 
                           tasks=tasks, 
                           tasks_pagination=tasks_pagination,
                           current_search_query=search_query,
                           current_filter_status=status_filter,
                           current_filter_priority=priority_filter,
                           current_due_date_filter=due_date_filter,
                           current_category_filter=category_filter, # NOVO: Passar para o template
                           current_sort_by=sort_by,
                           current_order=order,
                           today=today,
                           all_categories=all_categories # NOVO: Passar categorias para o template
                        )

# Rota para criar tarefa (MODIFICADA para incluir category)
@app.route('/create', methods=['POST'])
@login_required
def create_task():
    description = request.form['description']
    priority = request.form['priority']
    due_date_str = request.form['due_date']
    category = request.form.get('category') # NOVO: Captura a categoria (pode ser None)
    
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de data de vencimento inválido.', 'danger')
            return redirect(url_for('index'))

    # NOVO: Limpar categoria se for string vazia
    if category == '':
        category = None

    new_task = Task(description=description, priority=priority, due_date=due_date, category=category, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    flash('Tarefa criada com sucesso!', 'success')
    return redirect(url_for('index'))

# Rota para completar tarefa
@app.route('/complete/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('Você não tem permissão para modificar esta tarefa.', 'danger')
        return redirect(url_for('index'))
    task.completed = not task.completed
    db.session.commit()
    flash('Status da tarefa atualizado!', 'success')
    return redirect(url_for('index'))

# Rota para atualizar tarefa (MODIFICADA para incluir category)
@app.route('/update/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('Você não tem permissão para modificar esta tarefa.', 'danger')
        return redirect(url_for('index'))
    
    task.description = request.form['description']
    task.priority = request.form['priority']
    due_date_str = request.form['due_date']
    category = request.form.get('category') # NOVO: Captura a categoria

    if due_date_str:
        try:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de data de vencimento inválido.', 'danger')
            return redirect(url_for('index'))
    else:
        task.due_date = None
    
    # NOVO: Limpar categoria se for string vazia
    if category == '':
        task.category = None
    else:
        task.category = category

    db.session.commit()
    flash('Tarefa atualizada com sucesso!', 'success')
    return redirect(url_for('index'))

# Rota para deletar tarefa
@app.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('Você não tem permissão para deletar esta tarefa.', 'danger')
        return redirect(url_for('index'))
    db.session.delete(task)
    db.session.commit()
    flash('Tarefa deletada com sucesso!', 'success')
    return redirect(url_for('index'))

# Filtro Jinja para formatar data e hora
@app.template_filter('localdatetime')
def localdatetime_filter(dt):
    if dt is None:
        return 'N/A'
    return dt.strftime('%d/%m/%Y às %H:%M:%S')

@app.template_filter('localdate')
def localdate_filter(d):
    if d is None:
        return 'N/A'
    return d.strftime('%d/%m/%Y')


if __name__ == '__main__':
    app.run(debug=True)