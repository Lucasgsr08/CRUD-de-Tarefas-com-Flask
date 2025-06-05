from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Email
from flask_wtf import FlaskForm
from datetime import datetime # Importar datetime
import pytz # <--- Nova importação para fusos horários

# Criando a aplicação Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'abc123'
db = SQLAlchemy(app)

# Definindo o fuso horário local (Goiânia/São Paulo)
# Use 'America/Sao_Paulo' que cobre boa parte do Brasil, incluindo Goiás
LOCAL_TIMEZONE = pytz.timezone('America/Sao_Paulo')

# Definindo o modelo de dados
class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), unique=True, nullable=False)
    # created_at armazena a hora UTC
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}: {self.description}>'

# Formulário de Registro (mantido como exemplo)
class RegisterForm(FlaskForm):
    first_name = StringField('Primeiro Nome', validators=[DataRequired()])
    last_name = StringField('Sobrenome')
    email = StringField('Email', validators=[Email(message='E-mail inválido!')])
    password = PasswordField('Senha', validators=[InputRequired(), EqualTo('confirm', message='As senhas devem ser iguais!')])
    confirm = PasswordField('Confirme a senha')
    submit = SubmitField('CADASTRAR')


# CRUD - Read (Rota principal)
@app.route('/')
def index():
    tasks = Tasks.query.order_by(Tasks.created_at.desc()).all()
    # Converter created_at para o fuso horário local antes de enviar para o template
    for task in tasks:
        # Se task.created_at não tiver informações de fuso horário (naive datetime),
        # force-o a ser UTC antes de converter. Isso é comum com datetime.utcnow().
        if task.created_at.tzinfo is None:
            utc_dt = pytz.utc.localize(task.created_at)
        else:
            utc_dt = task.created_at

        task.local_created_at = utc_dt.astimezone(LOCAL_TIMEZONE)
    return render_template('index.html', tasks=tasks)

# CRUD - Create (sem mudanças, pois created_at já usa utcnow)
@app.route('/create_task', methods=['POST'])
def create_task():
    if request.method == 'POST':
        description = request.form.get('description')

        if not description:
            flash("A descrição da tarefa não pode ser vazia!", "error")
            return redirect(url_for('index'))

        existing_task = Tasks.query.filter_by(description=description).first()
        if existing_task:
            flash("Essa tarefa já existe!", "error")
        else:
            try:
                new_task = Tasks(description=description)
                db.session.add(new_task)
                db.session.commit()
                flash("Tarefa criada com sucesso!", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao criar tarefa: {e}", "error")
    return redirect(url_for('index'))

# CRUD - Delete
@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task_to_delete = Tasks.query.get_or_404(task_id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        flash("Tarefa excluída com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir tarefa: {e}", "error")
    return redirect(url_for('index'))

# CRUD - Update
@app.route('/update_task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    task_to_update = Tasks.query.get_or_404(task_id)
    if request.method == 'POST':
        new_description = request.form.get('description')

        if not new_description:
            flash("A descrição da tarefa não pode ser vazia ao atualizar!", "error")
            return redirect(url_for('index'))

        existing_task = Tasks.query.filter(Tasks.description == new_description, Tasks.id != task_id).first()
        if existing_task:
            flash("Já existe uma tarefa com essa descrição!", "error")
        else:
            try:
                task_to_update.description = new_description
                db.session.commit()
                flash("Tarefa atualizada com sucesso!", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao atualizar tarefa: {e}", "error")
    return redirect(url_for('index'))

# Rota de Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        flash("Usuário registrado com sucesso!", "success")
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


# Executando o servidor e criando as tabelas do banco de dados
if __name__ == '__main__':
    with app.app_context():
        # Lembre-se: se você adicionou o campo created_at anteriormente e já tem um site.db,
        # você precisará deletar site.db (e a pasta instance se existir) e rodar novamente.
        db.create_all()
    app.run(debug=True, port=5153)