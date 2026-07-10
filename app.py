import os
from datetime import datetime, timedelta, date
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session
)

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


app = Flask(__name__)


# =========================
# CONFIGURAÇÕES
# =========================

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "sigea_secret_key_v2"
)


BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)


database_url = os.getenv("DATABASE_URL")


if database_url:

    database_url = database_url.replace(
        "postgres://",
        "postgresql://"
    )

else:

    database_url = (
        "sqlite:///"
        + os.path.join(
            BASE_DIR,
            "sigea_v2.db"
        )
    )


app.config["SQLALCHEMY_DATABASE_URI"] = database_url

app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = False


db = SQLAlchemy(app)



# =========================
# MODELOS
# =========================


class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    senha = db.Column(
        db.String(200),
        nullable=False
    )

    tipo = db.Column(
        db.String(20),
        nullable=False
    )


    agendamentos = db.relationship(
        "Agendamento",
        backref="professor",
        lazy=True
    )



class Laboratorio(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(100),
        nullable=False
    )


    categoria = db.Column(
        db.String(50),
        nullable=False
    )


    capacidade = db.Column(
        db.Integer
    )


    agendamentos = db.relationship(
        "Agendamento",
        backref="lab",
        lazy=True
    )



class Agendamento(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )


    instrutor = db.Column(
        db.String(100),
        nullable=False
    )


    lab_id = db.Column(
        db.Integer,
        db.ForeignKey("laboratorio.id"),
        nullable=False
    )


    turma = db.Column(
        db.String(50),
        nullable=False
    )


    data = db.Column(
        db.Date,
        nullable=False
    )


    turno = db.Column(
        db.String(20),
        nullable=False
    )


    num_alunos = db.Column(
        db.Integer
    )


    status = db.Column(
        db.String(20),
        default="Pendente"
    )


    data_criacao = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )



# =========================
# INICIALIZAÇÃO DO BANCO
# =========================


def inicializar_banco():

    db.create_all()


    # Criar laboratórios somente se estiver vazio

    if Laboratorio.query.count() == 0:


        laboratorios = {


            "Informática": [
                "Laboratório Grande",
                "Laboratório Pequeno"
            ],


            "Elétrica": [
                "Predial",
                "Industrial",
                "PLC",
                "Ensaios Elétricos",
                "Eletrônica",
                "SEP - Externo",
                "Renováveis"
            ],


            "Mecânica": [
                "Manutenção",
                "Hidráulica",
                "Pneumática",
                "Ferramentaria",
                "Tornearia",
                "Caldeiraria",
                "Solda",
                "Metrologia",
                "Metalografia"
            ],


            "Outros": [
                "Auditório",
                "Sala Maker"
            ]

        }


        for categoria, nomes in laboratorios.items():

            for nome in nomes:

                db.session.add(
                    Laboratorio(
                        nome=nome,
                        categoria=categoria,
                        capacidade=25
                    )
                )


    # Criar usuário administrador

    if not User.query.filter_by(
        email="admin@senai.br"
    ).first():


        admin = User(

            nome="Supervisor SENAI",

            email="admin@senai.br",

            senha=generate_password_hash(
                "admin123"
            ),

            tipo="supervisor"

        )


        db.session.add(admin)


    db.session.commit()



with app.app_context():

    inicializar_banco()



# =========================
# HELPERS
# =========================


def get_semana_limite():

    hoje = date.today()

    inicio = hoje - timedelta(
        days=hoje.weekday()
    )

    fim = inicio + timedelta(
        days=13
    )

    return inicio, fim



def admin_required(func):

    @wraps(func)

    def wrapper(*args, **kwargs):

        if (
            "user_id" not in session
            or session.get("user_tipo")
            != "supervisor"
        ):

            flash(
                "Acesso restrito.",
                "danger"
            )

            return redirect(
                url_for("login")
            )


        return func(
            *args,
            **kwargs
        )


    return wrapper



# =========================
# ROTAS
# =========================


@app.route("/")
def index():

    return redirect(
        url_for("calendario")
    )



@app.route(
    "/login",
    methods=["GET","POST"]
)
def login():


    if "user_id" in session:

        return redirect(
            url_for("admin_resumo")
        )


    if request.method == "POST":


        email = request.form.get(
            "email"
        )

        senha = request.form.get(
            "senha"
        )


        user = User.query.filter_by(
            email=email
        ).first()



        if (
            user
            and check_password_hash(
                user.senha,
                senha
            )
            and user.tipo=="supervisor"
        ):


            session["user_id"] = user.id

            session["user_nome"] = user.nome

            session["user_tipo"] = user.tipo


            return redirect(
                url_for(
                    "admin_resumo"
                )
            )



        flash(
            "Login inválido.",
            "danger"
        )


    return render_template(
        "login.html"
    )



@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )



@app.route("/calendario")
def calendario():

    categorias = {

        "Informática":
            Laboratorio.query.filter_by(
                categoria="Informática"
            ).all(),


        "Elétrica":
            Laboratorio.query.filter_by(
                categoria="Elétrica"
            ).all(),


        "Mecânica":
            Laboratorio.query.filter_by(
                categoria="Mecânica"
            ).all(),


        "Outros":
            Laboratorio.query.filter_by(
                categoria="Outros"
            ).all()

    }


    inicio, fim = get_semana_limite()


    return render_template(
        "calendario_v2.html",
        categorias=categorias,
        data_min=inicio,
        data_max=fim
    )



@app.route("/api/eventos")
def api_eventos():


    turno = request.args.get(
        "turno",
        "Matutino"
    )


    dados = Agendamento.query.filter_by(
        turno=turno
    ).all()


    eventos=[]


    for a in dados:


        cor = (

            "#198754"
            if a.status=="Confirmado"

            else "#ffc107"
            if a.status=="Pendente"

            else "#dc3545"

        )


        eventos.append({

            "id":a.id,

            "title":
                f"{a.lab.nome} - {a.turma}",

            "start":
                a.data.isoformat(),

            "backgroundColor":
                cor,

            "borderColor":
                cor,


            "extendedProps":{

                "professor":
                    a.instrutor,

                "status":
                    a.status,

                "lab":
                    a.lab.nome,

                "alunos":
                    a.num_alunos
            }

        })


    return jsonify(eventos)



@app.route(
    "/agendar",
    methods=["POST"]
)
def agendar():


    data_agend = datetime.strptime(
        request.form.get("data"),
        "%Y-%m-%d"
    ).date()



    inicio,fim = get_semana_limite()



    if data_agend < inicio or data_agend > fim:

        return jsonify({

            "success":False,

            "message":
            "Data fora do período permitido."

        }),400



    novo = Agendamento(

        instrutor=request.form.get(
            "instrutor"
        ),

        lab_id=request.form.get(
            "lab_id"
        ),

        turma=request.form.get(
            "turma"
        ),

        data=data_agend,

        turno=request.form.get(
            "turno"
        ),

        num_alunos=request.form.get(
            "num_alunos"
        )

    )



    db.session.add(novo)

    db.session.commit()



    return jsonify({

        "success":True,

        "message":
        "Solicitação enviada."

    })



@app.route("/admin/resumo")
@admin_required
def admin_resumo():

    hoje=date.today()

    inicio=hoje-timedelta(
        days=hoje.weekday()
    )


    dias=[

        inicio+timedelta(days=i)

        for i in range(5)

    ]


    resumo={}


    for d in dias:

        resumo[d]={

            "Matutino":
            Agendamento.query.filter_by(
                data=d,
                turno="Matutino",
                status="Confirmado"
            ).all(),


            "Vespertino":
            Agendamento.query.filter_by(
                data=d,
                turno="Vespertino",
                status="Confirmado"
            ).all(),


            "Noturno":
            Agendamento.query.filter_by(
                data=d,
                turno="Noturno",
                status="Confirmado"
            ).all()

        }



    return render_template(
        "admin_resumo.html",
        resumo=resumo
    )



@app.route(
    "/admin/acao/<int:id>/<string:acao>",
    methods=["POST"]
)
@admin_required
def admin_acao(id,acao):


    agendamento = Agendamento.query.get_or_404(id)


    if acao=="aprovar":

        agendamento.status="Confirmado"


    elif acao=="rejeitar":

        agendamento.status="Recusado"


    elif acao=="excluir":

        db.session.delete(
            agendamento
        )


    db.session.commit()


    return jsonify(
        {"success":True}
    )


