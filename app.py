from flask import Flask, render_template
from flask import request
from flask import abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, ForeignKey
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user,  login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, jsonify
import json
import requests
from os import environ

Base = declarative_base()
app = Flask(__name__)
DB_HOST = environ.get('DB_HOST', default='sql10.freemysqlhosting.net')
DB_NAME = environ.get('DB_NAME', default='sql10404637')
DB_PASSWORD = environ.get('DB_PASSWORD', default='HXPT7824Gj')
DB_USERNAME = environ.get('DB_USERNAME', default='sql10404637')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
login_manager = LoginManager(app)
db = SQLAlchemy(app)


@login_manager.user_loader
def get_user(user_id):
    return Usuario.query.filter_by(id=user_id).first()


class Pessoa(db.Model, Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), unique=True)
    nome = db.Column(db.String(80))
    telefone = db.Column(db.String(80))
    data_de_nascimento = db.Column(db.String(80))
    cpf = db.Column(db.String(80), unique=True)

    def __init__(self, email, nome, telefone, data_de_nascimento, cpf):
        self.email = email
        self.nome = nome
        self.telefone = telefone
        self.data_de_nascimento = data_de_nascimento
        self.cpf = cpf


class Empresa(db.Model, Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), unique=True)
    nome = db.Column(db.String(80))
    token = db.Column(db.String(80), unique=True)
    creditos = db.Column(db.Integer())

    def __init__(self, email, nome, creditos, token):
        self.email = email
        self.nome = nome
        self.token = token
        self.creditos = creditos


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), unique=True)
    senha = db.Column(db.String(255))

    def __init__(self, email, senha):
        self.email = email
        self.senha = senha

    def verify_password(self, password):
        return self.senha == generate_password_hash(password, method='sha256')


@app.route('/')
def home():

    return render_template("home.html", messages=False)


@app.route('/pessoa_publica')
def pessoa():
    data = Pessoa.query.all()
    return render_template("pessoa_publica.html", data=data)\



@app.route('/empresa')
def empresa():
    data = Empresa.query.all()
    return render_template("empresa.html", data=data)


@app.route('/registrando_pessoa', methods=['POST'])
def registrando_pessoa():
    if request.method == 'POST':
        try:
            pessoa_existente = db.session.query(Pessoa).filter(Pessoa.cpf == request.form['cpf']).one()
            pessoa_existente.nome = request.form['nome']
            pessoa_existente.email = request.form['email']
            pessoa_existente.telefone = request.form['telefone']
            pessoa_existente.data_de_nascimento = request.form['data_de_nascimento']
            pessoa_existente.cpf = request.form['cpf']
            db.session.commit()

        except NoResultFound:
            registrando_pessoa = Pessoa(email=request.form['email'], nome=request.form['nome'], telefone=request.form['telefone'], data_de_nascimento=request.form['data_de_nascimento'], cpf=request.form['cpf'])
            db.session.add(registrando_pessoa)
            db.session.commit()

        return redirect(url_for('home'))


@app.route('/registrando_empresa', methods=['POST'])
def registrando_empresa():
    if request.method == 'POST':
        registrando_empresa = Empresa(email=request.form['email'], nome=request.form['nome'], token=request.form['token'], creditos=request.form['creditos'])
        db.session.add(registrando_empresa)
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/registrando_usuario', methods=['POST'])
def registrando_usuario():
    if request.method == 'POST':
        password = generate_password_hash(request.form['senha'], method='sha256')
        registrando_usuario = Usuario(email=request.form['email'],  senha=password)
        db.session.add(registrando_usuario)
        db.session.commit()
        return redirect(url_for('tabela_usuario'))


@app.route("/cadastrar_pessoa")
def cadastrar_pessoa():
    return render_template("cadastrar_pessoa.html", messages=False)


@app.route("/criador_de_usuario")
def criador_de_usuario():
    return render_template("criador_de_usuario.html", messages=False)


@app.route("/cadastrar_empresa")
def cadastrar_empresa():
    return render_template("cadastrar_empresa.html", messages=False)


@app.route("/login_usuario")
def login_usuario():
    return render_template("login_usuario.html", messages=False)


@app.route("/tabela_pessoa")
def tabela_pessoa():
    data = Pessoa.query.all()
    return render_template("crud_pessoas.html", messages=False, data=data)


@app.route("/tabela_empresa")
def tabela_empresa():
    data = Empresa.query.all()
    return render_template("crud_empresas.html", messages=False, data=data)


@app.route("/tabela_usuario")
def tabela_usuario():
    data = Usuario.query.all()
    return render_template("crud_usuario.html", messages=False, data=data)


@app.route('/deletar_pessoa/<int:id>')
def deletar_pessoa(id):
    delete_pessoa = Pessoa.query.get(id)
    db.session.delete(delete_pessoa)
    db.session.commit()
    return redirect(url_for("tabela_pessoa"))\



@app.route('/deletar_empresa/<int:id>')
def deletar_empresa(id):
    delete_empresa = Empresa.query.get(id)
    db.session.delete(delete_empresa)
    db.session.commit()
    return redirect(url_for("tabela_empresa"))


@app.route('/deletar_usuario/<int:id>')
def deletar_usuario(id):
    delete_usuario = Usuario.query.get(id)
    db.session.delete(delete_usuario)
    db.session.commit()
    return redirect(url_for("tabela_usuario"))


@app.route('/editar_empresa/<int:id>', methods=['GET', 'POST'])
def editar_empresa(id):
    data = Empresa.query.get(id)
    if request.method == 'POST':
        data.nome = request.form['nome']
        data.email = request.form['email']
        data.token = request.form['token']
        data.creditos = request.form['creditos']
        db.session.commit()
        return redirect(url_for('tabela_empresa'))
    return render_template("editar_empresa.html", data=data)


@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    data = Usuario.query.get(id)
    if request.method == 'POST':
        data.email = request.form['email']
        data.senha = generate_password_hash(request.form['senha'], method='sha256')
        db.session.commit()
        return redirect(url_for('tabela_usuario'))
    return render_template("editar_usuario.html", data=data)


@app.route('/editar_pessoa/<int:id>', methods=['GET', 'POST'])
def editar_pessoa(id):
    data = Pessoa.query.get(id)
    if request.method == 'POST':
        data.nome = request.form['nome']
        data.email = request.form['email']
        data.telefone = request.form['telefone']
        data.data_de_nascimento = request.form['data_de_nascimento']
        data.cpf = request.form['cpf']
        db.session.commit()
        return redirect(url_for('tabela_pessoa'))
    return render_template("editar_pessoa.html", data=data)


@app.route('/esqueci_senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form['email']
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login("joaoricardoroma@gmail.com", "lfujqcilgfgkmavp")
        server.sendmail("joaoricardoroma@gmail.com",
                        f"{email}",
                        "hello,Your password is 123")
        server.quit()
        return render_template("login_usuario.html")
    return render_template("esqueci_senha.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['senha']
        user = Usuario.query.filter_by(email=email).first()
        if not user or not user.verify_password(password):
            return redirect(url_for("login"))

        login_user(user)
        return redirect(url_for("logado"))
    return render_template("login_usuario.html")


@app.route('/logado')
@login_required
def logado():
    return render_template("logado.html")


@app.route('/api/consult_by_phone', methods=['POST'])
def consult_by_phone():
    try:
        token = request.headers.get('Authorization')
        token = token.replace("Bearer ", "")
        empresa = Empresa.query.filter(Empresa.token == token) \
            .filter(Empresa.creditos >= 1) \
            .one()
    except NoResultFound:
        return abort(400, description="")

    try:
        pessoa_filtrada = Pessoa.query.filter_by(telefone=request.form['phone']).first()
        _return = {
            'nome': f'{pessoa_filtrada.nome}'
        }
        empresa.creditos -= 1
        db.session.commit()

        return jsonify(_return)
    except AttributeError:
        return abort(404, description="")


@app.route('/api/consult_by_screen', methods=['GET', 'POST'])
def consult_by_screen():
    data = None
    if request.method == 'POST':
        url = 'http://127.0.0.1:5000/api/consult_by_phone'
        headers = {'Authorization': 'Bearer 123'}
        payload = {'phone': '{}'.format(request.form['phone'])}
        request_api = requests.post(url, data=payload, headers=headers)
        if request_api.status_code == 200:
            data = f"Nome da pessoa consultada e {request_api.json()['nome']}"
        else:
            data = "Dados inseridos incorretos"
    return render_template("consult_by_screen.html", data=data)