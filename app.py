from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'mysql+pymysql://user:password@localhost/project_management_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# --- Modelos de Dados ---
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='Pendente') # Pendente, Em Progresso, Concluído

    tasks = db.relationship('Task', backref='project', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.name}>"

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='Pendente') # Pendente, Em Progresso, Concluída
    due_date = db.Column(db.Date)
    priority = db.Column(db.String(20), default='Média') # Baixa, Média, Alta

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    assigned_members = db.relationship('TaskAssignment', backref='task', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task {self.name}>"

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50))

    assigned_tasks = db.relationship('TaskAssignment', backref='member', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Member {self.name}>"

class TaskAssignment(db.Model):
    __tablename__ = 'task_assignment'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('task_id', 'member_id', name='uq_task_member'),
    )

    def __repr__(self):
        return f"<TaskAssignment Task:{self.task_id} Member:{self.member_id}>"



# --- Rotas da Aplicação ---

@app.route('/')
def index():
    return render_template('index.html')

# --- Rotas para Projetos ---
@app.route('/projects')
def projects():
    all_projects = Project.query.all()
    return render_template('projects.html', projects=all_projects)

@app.route('/project/new', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        status = request.form['status']

        new_project = Project(name=name, description=description, start_date=start_date, end_date=end_date, status=status)
        db.session.add(new_project)
        db.session.commit()
        flash('Projeto criado com sucesso!', 'success')
        return redirect(url_for('projects'))
    return render_template('create_project.html')

@app.route('/project/edit/<int:id>', methods=['GET', 'POST'])
def edit_project(id):
    project = Project.query.get_or_404(id)
    if request.method == 'POST':
        project.name = request.form['name']
        project.description = request.form['description']
        project.start_date = request.form['start_date']
        project.end_date = request.form['end_date']
        project.status = request.form['status']
        db.session.commit()
        flash('Projeto atualizado com sucesso!', 'success')
        return redirect(url_for('projects'))
    return render_template('edit_project.html', project=project)

@app.route('/project/delete/<int:id>', methods=['POST'])
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Projeto excluído com sucesso!', 'success')
    return redirect(url_for('projects'))

# --- Rotas para Tarefas ---
@app.route('/tasks')
def tasks():
    all_tasks = Task.query.all()
    return render_template('tasks.html', tasks=all_tasks)

@app.route('/task/new/<int:project_id>', methods=['GET', 'POST'])
@app.route('/task/new', methods=['GET', 'POST'])
def create_task(project_id=None):
    projects_list = Project.query.all()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        status = request.form['status']
        due_date = request.form['due_date']
        priority = request.form['priority']
        project_id_form = request.form['project_id']

        new_task = Task(name=name, description=description, status=status, due_date=due_date, priority=priority, project_id=project_id_form)
        db.session.add(new_task)
        db.session.commit()
        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('tasks'))
    return render_template('create_task.html', projects=projects_list, selected_project_id=project_id)

@app.route('/task/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get_or_404(id)
    projects_list = Project.query.all()
    if request.method == 'POST':
        task.name = request.form['name']
        task.description = request.form['description']
        task.status = request.form['status']
        task.due_date = request.form['due_date']
        task.priority = request.form['priority']
        task.project_id = request.form['project_id']
        db.session.commit()
        flash('Tarefa atualizada com sucesso!', 'success')
        return redirect(url_for('tasks'))
    return render_template('edit_task.html', task=task, projects=projects_list)

@app.route('/task/delete/<int:id>', methods=['POST'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    flash('Tarefa excluída com sucesso!', 'success')
    return redirect(url_for('tasks'))

# --- Rotas para Membros da Equipe ---
@app.route('/members')
def members():
    all_members = Member.query.all()
    return render_template('members.html', members=all_members)

@app.route('/member/new', methods=['GET', 'POST'])
def create_member():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        new_member = Member(name=name, email=email, role=role)
        db.session.add(new_member)
        db.session.commit()
        flash('Membro da equipe criado com sucesso!', 'success')
        return redirect(url_for('members'))
    return render_template('create_member.html')

@app.route('/member/edit/<int:id>', methods=['GET', 'POST'])
def edit_member(id):
    member = Member.query.get_or_404(id)
    if request.method == 'POST':
        member.name = request.form['name']
        member.email = request.form['email']
        member.role = request.form['role']
        db.session.commit()
        flash('Membro da equipe atualizado com sucesso!', 'success')
        return redirect(url_for('members'))
    return render_template('edit_member.html', member=member)

@app.route('/member/delete/<int:id>', methods=['POST'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    flash('Membro da equipe excluído com sucesso!', 'success')
    return redirect(url_for('members'))

# --- Rotas para Atribuição de Tarefas (N:N) ---
@app.route('/assign_task', methods=['GET', 'POST'])
def assign_task():
    tasks_list = Task.query.all()
    members_list = Member.query.all()
    if request.method == 'POST':
        task_id = request.form['task_id']
        member_id = request.form['member_id']

        # Verificar se a atribuição já existe
        existing_assignment = TaskAssignment.query.filter_by(task_id=task_id, member_id=member_id).first()
        if existing_assignment:
            flash('Este membro já está atribuído a esta tarefa!', 'warning')
        else:
            new_assignment = TaskAssignment(task_id=task_id, member_id=member_id)
            db.session.add(new_assignment)
            db.session.commit()
            flash('Tarefa atribuída com sucesso!', 'success')
        return redirect(url_for('assign_task'))

    # Para exibir as atribuições existentes
    current_assignments = TaskAssignment.query.all()
    return render_template('assign_task.html', tasks=tasks_list, members=members_list, assignments=current_assignments)

@app.route('/assign_task/delete/<int:assignment_id>', methods=['POST'])
def delete_assignment(assignment_id):
    assignment = TaskAssignment.query.get_or_404(assignment_id)
    db.session.delete(assignment)
    db.session.commit()
    flash('Atribuição removida com sucesso!', 'success')
    return redirect(url_for('assign_task'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Cria as tabelas se não existirem (apenas para desenvolvimento inicial)
    app.run(debug=True)