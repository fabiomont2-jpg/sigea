import os
from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "sigea_secret_key_v2"
)

database_url = os.environ.get(
    "DATABASE_URL",
    "sqlite:///sigea.db"
)

# Compatibilidade com PostgreSQL do Render
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Modelos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), nullable=False) # 'professor' ou 'supervisor'
    agendamentos = db.relationship('Agendamento', backref='professor', lazy=True)

class Laboratorio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False) # Informática, Elétrica, Mecânica, Outros
    capacidade = db.Column(db.Integer)
    agendamentos = db.relationship('Agendamento', backref='lab', lazy=True)

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    instrutor = db.Column(db.String(100), nullable=False)
    lab_id = db.Column(db.Integer, db.ForeignKey('laboratorio.id'), nullable=False)
    turma = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date, nullable=False)
    turno = db.Column(db.String(20), nullable=False) # Matutino, Vespertino, Noturno
    num_alunos = db.Column(db.Integer)
    status = db.Column(db.String(20), default='Pendente') # Pendente, Confirmado, Recusado
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

# Helpers
def get_semana_limite():
    hoje = date.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_proxima_semana = inicio_semana + timedelta(days=13)
    return inicio_semana, fim_proxima_semana

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_tipo') != 'supervisor':
            flash('Acesso restrito a administradores.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rotas
# No app.py, substitua as rotas '/' e '/login' por estas:

@app.route('/')
def index():
    return redirect(url_for('calendario'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('admin_resumo'))
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.senha, senha) and user.tipo == 'supervisor':
            session['user_id'] = user.id
            session['user_nome'] = user.nome
            session['user_tipo'] = user.tipo
            return redirect(url_for('admin_resumo'))
        flash('Credenciais inválidas ou sem permissão de administrador.', 'danger')
    return render_template('login.html')




@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/calendario')
def calendario():
    labs = Laboratorio.query.all()
    categorias = {
        'Informática': Laboratorio.query.filter_by(categoria='Informática').all(),
        'Elétrica': Laboratorio.query.filter_by(categoria='Elétrica').all(),
        'Mecânica': Laboratorio.query.filter_by(categoria='Mecânica').all(),
        'Outros': Laboratorio.query.filter_by(categoria='Outros').all(),
    }
    ini, fim = get_semana_limite()
    return render_template('calendario_v2.html', categorias=categorias, data_min=ini, data_max=fim)

@app.route('/api/eventos')
def api_eventos():
    turno = request.args.get('turno', 'Matutino')
    agendamentos = Agendamento.query.filter_by(turno=turno).all()
    eventos = []
    for a in agendamentos:
        cor = '#198754' if a.status == 'Confirmado' else '#ffc107' if a.status == 'Pendente' else '#dc3545'
        eventos.append({
            'id': a.id,
            'title': f"{a.lab.nome} - {a.turma}",
            'start': a.data.isoformat(),
            'backgroundColor': cor,
            'borderColor': cor,
            'extendedProps': {
                'professor': a.instrutor,
                'status': a.status,
                'lab': a.lab.nome,
                'alunos': a.num_alunos
            }
        })
    return jsonify(eventos)

@app.route('/agendar', methods=['POST'])
def agendar():
    data_str = request.form.get('data')
    data_agend = datetime.strptime(data_str, '%Y-%m-%d').date()
    ini, fim = get_semana_limite()
    
    if data_agend < ini or data_agend > fim:
        return jsonify({'success': False, 'message': 'Data fora do período permitido (semana atual e próxima).'}), 400

    novo = Agendamento(
        instrutor=request.form.get('instrutor'),
        lab_id=request.form.get('lab_id'),
        turma=request.form.get('turma'),
        data=data_agend,
        turno=request.form.get('turno'),
        num_alunos=request.form.get('num_alunos'),
        status='Pendente'
    )
    db.session.add(novo)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Solicitação enviada com sucesso!'})

@app.route('/admin/resumo')
@admin_required
def admin_resumo():
    hoje = date.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    dias_semana = [inicio_semana + timedelta(days=i) for i in range(5)] # Seg a Sex
    
    resumo = {}
    for d in dias_semana:
        resumo[d] = {
            'Matutino': Agendamento.query.filter_by(data=d, turno='Matutino', status='Confirmado').all(),
            'Vespertino': Agendamento.query.filter_by(data=d, turno='Vespertino', status='Confirmado').all(),
            'Noturno': Agendamento.query.filter_by(data=d, turno='Noturno', status='Confirmado').all(),
        }
    return render_template('admin_resumo.html', resumo=resumo)

@app.route('/admin/acao/<int:id>/<string:acao>', methods=['POST'])
@admin_required
def admin_acao(id, acao):
    agend = Agendamento.query.get_or_404(id)
    if acao == 'aprovar': agend.status = 'Confirmado'
    elif acao == 'rejeitar': agend.status = 'Recusado'
    elif acao == 'excluir': db.session.delete(agend)
    db.session.commit()
    return jsonify({'success': True})

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
