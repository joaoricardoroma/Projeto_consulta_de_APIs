from flask import Flask, render_template
from flask import request
from flask import abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, ForeignKey

Base = declarative_base()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123@127.0.0.1/investment'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Pessoa(db.Model, Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), unique=True)
    nome = db.Column(db.String(80))
    telefone = db.Column(db.String(80))
    data_de_nascimento = db.Column(db.String(80))
    cpf = db.Column(db.String(80), unique=True)
    senha = db.Column(db.String(80))

    def __init__(self, email, nome, telefone, data_de_nascimento, cpf, senha):
        self.email = email
        self.senha = senha
        self.nome = nome
        self.telefone = telefone
        self.data_de_nascimento = data_de_nascimento
        self.cpf = cpf


class Empresa(db.Model, Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), unique=True)
    nome = db.Column(db.String(80))
    token = db.Column(db.String(80), unique=True)
    senha = db.Column(db.String(80))
    creditos = db.Column(db.Integer())

    def __init__(self, email, nome, senha, creditos, token):
        self.email = email
        self.senha = senha
        self.nome = nome
        self.token = token
        self.creditos = creditos


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
            pessoa_existente.senha = request.form['senha']
            db.session.commit()

        except NoResultFound:
            registrando_pessoa = Pessoa(email=request.form['email'],  senha=request.form['senha'], nome=request.form['nome'], telefone=request.form['telefone'], data_de_nascimento=request.form['data_de_nascimento'], cpf=request.form['cpf'])
            db.session.add(registrando_pessoa)
            db.session.commit()

        return redirect(url_for('home'))


@app.route('/registrando_empresa', methods=['POST'])
def registrando_empresa():
    if request.method == 'POST':
        try:
            empresa_existente = db.session.query(Empresa).filter(Empresa.token == request.form['token']).one()
            empresa_existente.nome = request.form['nome']
            empresa_existente.email = request.form['email']
            empresa_existente.creditos = request.form['creditos']
            empresa_existente.token = request.form['token']
            empresa_existente.senha = request.form['senha']
            db.session.commit()

        except NoResultFound:
            registrando_empresa = Empresa(email=request.form['email'],  senha=request.form['senha'], nome=request.form['nome'], token=request.form['token'], creditos=request.form['creditos'])
            db.session.add(registrando_empresa)
            db.session.commit()

        return redirect(url_for('home'))

@app.route("/cadastrar_pessoa")
def cadastrar_pessoa():
    return render_template("cadastrar_pessoa.html", messages=False)\


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

