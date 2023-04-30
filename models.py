
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt
from datetime import datetime
db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    senha = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '< Usuario%r>' % self.name

class Arquivo(db.Model):
    __tablename__ = 'arquivos'
    id = db.Column(db.Integer, primary_key=True)
    arquivo_csv = db.Column(db.LargeBinary, unique=False, nullable=True)
    nome_arquivo = db.Column(db.String(80), unique=False, nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.now,nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    def __repr__(self):
        return '<Arquivo %r>' % self.usuario_id  