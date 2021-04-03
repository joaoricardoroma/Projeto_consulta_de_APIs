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


@app.route('/')
def home():
    return render_template("home.html", messages=False)


@app.route('/pessoa_publica')
def pessoa():
    data = Pessoa.query.all()
    return render_template("pessoa_publica.html", data=data)


@app.route('/registrando', methods=['POST'])
def registrando():
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


@app.route("/cadastrar_pessoa")
def cadastrar_pessoa():
    return render_template("cadastrar_pessoa.html", messages=False)


@app.route("/verificando", methods=['POST'])
def verificando():
    return



@app.route("/entrar_pessoa")
def entrar_pessoa():
    return render_template("entrar_pessoa.html", messages=False)