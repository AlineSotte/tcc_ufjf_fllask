from flask import Flask, render_template,redirect, url_for,request,session, flash
from flask_paginate import Pagination, get_page_parameter
from models import db, Usuario, Arquivo
from datetime import datetime
from analise import Analise
from config import Config
import pandas as pd
import math
import io


app = Flask(__name__)

conf = Config()
instancia= Analise()

app.config.from_object(conf)
app.secret_key = conf.SECRET_KEY

## Criação para banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = conf.STRING_CONN
db.init_app(app)
with app.app_context():
    db.create_all()

app.config['SESSION_TYPE'] = conf.SESSION_TYPE
app.config['SESSION_FILE_DIR'] = conf.SESSION_FILE_DIR


@app.route('/')
def index():
    return redirect(url_for('login'))

## Login e Logof
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        user = db.session.query(Usuario).filter_by(email=email).first()
        if user.email==email and user.senha==password:
            session['username'] = request.form['username']
            return redirect(url_for('csv',id_usuario=user.id))
    else:
        # Login failed
        return render_template('login.html', error='Usuário ou senha inválidas')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.clear()
    return redirect(url_for('index'))

## download arquivo e gravar no banco de dados
@app.route('/csv/<int:id_usuario>', methods=['GET', 'POST'])
def csv(id_usuario):
    if request.method == 'POST':
        arquivo = request.files.get('arquivo_csv')
        if not arquivo:
            flash('Selecione um arquivo para enviar', 'error')
            return redirect(request.url)
        if not arquivo.filename.endswith('.csv'):
            flash('Selecione um arquivo CSV para enviar', 'error')
            return redirect(request.url)

        arquivo_bytes = arquivo.read()
        agora = datetime.now()
        data_hora = agora.strftime("%d%m%Y%H%M%S")
        nome_arq = f'arquivo_CSV_{data_hora}'

        if Arquivo.query.filter_by(nome_arquivo=nome_arq).first():
            flash('Este arquivo já foi enviado', 'error')
            return redirect(request.url)

        tabela_csv = Arquivo(usuario_id=id_usuario, arquivo_csv=arquivo_bytes, nome_arquivo=nome_arq)
        db.session.add(tabela_csv)
        db.session.commit()

        return redirect(url_for('dashboard', id_usuario=id_usuario, nome_arquivo=nome_arq))
    
    else:
        return render_template('csv.html', id_usuario=id_usuario)

## dashboard com paginação dando ruim pra carai
@app.route('/dashboard/<int:id_usuario>/<string:nome_arquivo>', methods=['GET'])
def dashboard(id_usuario, nome_arquivo):
    arquivo_csv = Arquivo.query.filter_by(nome_arquivo=nome_arquivo).first()
    dados_csv = arquivo_csv.arquivo_csv.decode('utf-8')
    df = pd.read_csv(io.StringIO(dados_csv))
    if df.empty:
        flash('O arquivo CSV está vazio', 'error')
        return redirect(url_for('csv', id_usuario=id_usuario))
    per_page = request.args.get('per_page', 10, type=int)
    num_pages = math.ceil(df.shape[0] / per_page)
    page = request.args.get('page', 1, type=int)
    current_page = page 
    page_links = [url_for('dashboard', id_usuario=id_usuario, nome_arquivo=nome_arquivo, page=p, per_page=per_page) for p in range(1, num_pages+1)]
    data = df[(page - 1) * per_page:page * per_page].to_dict(orient='records')
    return render_template('dashboard.html', data=data, page=page, per_page=per_page, current_page=current_page, page_links=page_links, num_pages=num_pages, nome_arquivo=nome_arquivo, id_usuario=id_usuario)

## Analise ##
@app.route('/analise/<int:id_usuario>/<string:nome_arquivo>', methods=['GET'])
def analise(id_usuario,nome_arquivo):
    arquivo_csv = Arquivo.query.filter_by(nome_arquivo=nome_arquivo).first()
    dados_csv = arquivo_csv.arquivo_csv.decode('utf-8')
    df = pd.read_csv(io.StringIO(dados_csv))
    situacao_aluno = instancia.mostrar_grafico_situacao_aluno(df)
    maior_reprovacao= instancia.calcular_diciplinas_maior_reprovacao(df)
    comp= instancia.mostrar_grafico_comparativo(df)
    data=df
    return render_template('analise.html', id_usuario=id_usuario,plot=situacao_aluno.to_html(full_html=False), maior_reprovacao=maior_reprovacao.to_html(classes='table table-striped'), comparativo=comp, data=data)
  
if __name__ == '__main__':
    app.run(debug=conf.DEBUG)


