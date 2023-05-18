from flask import Flask, render_template,redirect, url_for,request,session, flash, make_response
from werkzeug.utils import secure_filename
from models import db, Usuario, Arquivo
from datetime import datetime
from analise import Analise
from config import Config
import math

app = Flask(__name__, static_folder='static')

conf = Config()
instancia= Analise()

app.config.from_object(conf)
app.secret_key = conf.SECRET_KEY

## Criação para banco de dados/tabelas
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
        if email != '' and password != '':
            user = db.session.query(Usuario).filter_by(email=email).first()
            if user.email==email and user.senha==password:
                    session['username'] = request.form['username']
                    return redirect(url_for('csv_list',id_usuario=user.id))
            else:
                flash('E-mail ou senha incorretos', 'error')
                return redirect(request.url)
        else:
            flash('Preencha seu e-mail e senha', 'error')
            return redirect(request.url)
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

## download arquivo e gravar no banco de dados
## Listar 5 arquivos descending
@app.route('/dados_csv/<int:id_usuario>', methods=['GET', 'POST'])
def csv_list(id_usuario):
    
    arquivos = instancia.listar_cinco_arquivos(id_usuario)
    usuario_logado=Usuario.query.filter_by(id=id_usuario).first()
    
    if request.method == 'POST' and request.form.get('download_template') == 'true':
        template = Arquivo.query.filter_by(nome_arquivo='template_analise_2023_05_07_21_46_37.csv').first()
        response = make_response(template.arquivo_csv)
        response.headers['Content-Disposition'] = 'attachment; filename=template_analise.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response

    if request.method == 'POST':
        arquivo = request.files.get('arquivo_csv')
        if not arquivo:
            flash('Selecione um arquivo para enviar', 'error')
            return redirect(request.url)
        if not arquivo.filename.endswith('.csv'):
            flash('Selecione um arquivo CSV para enviar', 'error')
            return redirect(request.url)
        arquivo_bytes = arquivo.read()
        agora = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        arquivo_csv = arquivo.filename.split('.')[0] + '_'
        nome_arq = secure_filename(f"{arquivo_csv}{agora}.csv")
        if Arquivo.query.filter_by(nome_arquivo=nome_arq).first():
            flash('Este arquivo já foi enviado', 'error')
            return redirect(request.url)
        tabela_csv = Arquivo(usuario_id=id_usuario, arquivo_csv=arquivo_bytes, nome_arquivo=nome_arq)
        db.session.add(tabela_csv)
        db.session.commit()
        id = instancia.pegar_id(nome_arq)
        return redirect(url_for('dashboard', id_usuario=id_usuario, id=id))

    return render_template('csv.html', id_usuario=id_usuario, arquivos=arquivos, usuario_logado=usuario_logado.nome)
  
# paginação e download do arquivo
@app.route('/dashboard/<int:id_usuario>/<int:id>', methods=['GET'])
def dashboard(id_usuario, id):
    df = instancia.ler_ultimo_arquivo(id)
    meu_valor_padrao=''
    filtro = request.args.get('filtro',meu_valor_padrao)
    page = request.args.get('page', default=1, type=int)
    per_page = 5
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    if df.empty:
        flash('O arquivo CSV está vazio', 'error')
        return redirect(url_for('csv_list', id_usuario=id_usuario))
    elif filtro != '':
        busca = df[df['ALUNO'].astype(str).str.contains(filtro)].reset_index(drop=True)
        num_pages = len(busca) // per_page + 1
        data = busca.iloc[start_idx:end_idx]
    else:
        num_pages = len(df) // per_page + 1
        data = df.iloc[start_idx:end_idx]
    return render_template('dashboard.html', id_usuario=id_usuario,id=id,data=data, 
                           page=page, num_pages=num_pages, meu_valor_padrao=meu_valor_padrao)

## Analise ##
@app.route('/disciplina_reprovacao/<int:id_usuario>/<int:id>', methods=['GET'])
def disicplinas_reprovacao(id_usuario,id):
    df = instancia.ler_ultimo_arquivo(id)
    meu_valor_padrao=''
    filtro_ano = request.args.get('filtro_ano',meu_valor_padrao)
    selecionados = request.args.get('termo',meu_valor_padrao)
    periodo = request.args.get('filtro_periodo',meu_valor_padrao)
    maior_reprovacao= instancia.filtro_reprovacao(df,filtro_ano,selecionados,periodo)
    maior_reprovacao_html=maior_reprovacao.to_html(classes='table table-striped')
    return render_template('disicplinas_reprovacao.html',id_usuario=id_usuario,id=id,
                           maior_reprovacao=maior_reprovacao_html, meu_valor_padrao=meu_valor_padrao)

@app.route('/analise/<int:id_usuario>/<int:id>', methods=['GET'])
def analise(id_usuario,id):
    df = instancia.ler_ultimo_arquivo(id)
    meu_valor_padrao=''
    filtro = request.args.get('filtro',meu_valor_padrao)
    situacao_aluno = request.args.get('situacao',meu_valor_padrao)
    busca_aluno= instancia.filtro_alunos(df,filtro,situacao_aluno)
    page = request.args.get('page', default=1, type=int)
    per_page = 5
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    num_pages = math.ceil(len(busca_aluno) / per_page)
    filtro_pagina = busca_aluno.iloc[start_idx:end_idx]
    return render_template('analise.html', id_usuario=id_usuario,id=id,page=page,
                           busca_aluno=busca_aluno, meu_valor_padrao=meu_valor_padrao,
                           data=filtro_pagina,num_pages=num_pages,per_page=per_page)

@app.route('/grafico_comparativo/<int:id_usuario>/<int:id>', methods=['GET'])
def grafico_comparativo(id_usuario,id):
    df = instancia.ler_ultimo_arquivo(id)
    grafico = instancia.mostrar_grafico_comparativo(df)
    return render_template('grafico_comparativo.html', id_usuario=id_usuario,
                           id=id, grafico=grafico)

@app.route('/grafico_situacao_aluno/<int:id_usuario>/<int:id>', methods=['GET'])
def grafico_situacao_aluno(id_usuario,id):
    df = instancia.ler_ultimo_arquivo(id)
    grafico = instancia.mostrar_grafico_situacao_aluno(df).to_html(full_html=False)
    return render_template('grafico_situacao_aluno.html', id_usuario=id_usuario,
                           id=id, grafico=grafico)

@app.route('/analise_formandos/<int:id_usuario>/<int:id>', methods=['GET'])
def analise_formandos(id_usuario,id):
    df = instancia.ler_ultimo_arquivo(id)
    analise = instancia.analise_estatistica_formando(df).to_html(classes='table table-strip')
    analise2= instancia.analise_estatistica_formando_cotista(df).to_html(classes='table table-strip')
    analise3 = instancia.analise_estatistica_formando_n_cotista(df).to_html(classes='table table-strip')
    analise4 = instancia.analise_estatistica_formando_outros(df).to_html(classes='table table-strip')
    return render_template('analise_formandos.html', id_usuario=id_usuario,id=id,
                           analise=analise,analise2=analise2,analise3=analise3,analise4=analise4)
    
@app.route('/alunos_retidos/<int:id_usuario>/<int:id>', methods=['GET'])
def alunos_retidos(id_usuario, id):
    analise = instancia.analise_retidos(id)
    meu_valor_padrao=''
    filtro_ano= request.args.get('filtro_ano',meu_valor_padrao)
    page = request.args.get('page', default=1, type=int)
    per_page = 5
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    num_pages = math.ceil(len(analise) / per_page)
    if filtro_ano != '':
        busca = analise[analise['ANO ENTRADA'].astype(str).str.contains(filtro_ano)].reset_index(drop=True)
        num_pages = len(busca) // per_page + 1
        data = busca.iloc[start_idx:end_idx]
    else:
        num_pages = len(analise) // per_page + 1
        data = analise.iloc[start_idx:end_idx]
    grafico_analise_retido = instancia.grafico_retido_por_situacao(analise).to_html(full_html=False)
    return render_template('alunos_retidos.html', id_usuario=id_usuario, id=id,
                           data=data,num_pages=num_pages, page=page,
                           per_page=per_page,grafico_analise_retido=grafico_analise_retido)
    
@app.route('/analise_retidos/<int:id_usuario>/<int:id>', methods=['GET'])
def analise_retidos(id_usuario, id):
    arquivo_retidos = instancia.analise_retidos(id)
    analise = instancia.analise_estatistica_retido_total(arquivo_retidos).to_html(classes='table table-strip')
    analise1= instancia.analise_estatistica_retido_cotista(arquivo_retidos).to_html(classes='table table-strip')
    analise2 = instancia.analise_estatistica_retido_n_cotista(arquivo_retidos).to_html(classes='table table-strip')
    analise3 = instancia.analise_estatistica_retido_outros(arquivo_retidos).to_html(classes='table table-strip')
    return render_template('analise_retidos.html', id_usuario=id_usuario, id=id,
                           analise=analise, analise2=analise2, analise1=analise1,
                           analise3=analise3)
    
@app.route('/analise_evasao/<int:id_usuario>/<int:id>', methods=['GET'])
def analise_evasao(id_usuario, id):
    analise = instancia.analise_estatistica_evasao(id)
    analise1 = instancia.analise_estatistica_evasao_total(analise).to_html(classes='table table-strip')
    analise2 = instancia.analise_estatistica_evasao_cotista(analise).to_html(classes='table table-strip')
    analise3 = instancia.analise_estatistica_evasao_n_cotista(analise).to_html(classes='table table-strip')
    analise4= instancia.analise_estatistica_evasao_outros(analise).to_html(classes='table table-strip')
    return render_template('analise_evasao.html', id_usuario=id_usuario,
                           id=id, analise=analise, analise1=analise1,analise2=analise2,
                           analise3=analise3,analise4=analise4)


if __name__ == '__main__':
    app.run(debug=True)


