from flask import Flask, render_template,redirect, url_for,request,session, flash, make_response
from werkzeug.utils import secure_filename
from models import db, Usuario, Arquivo
from datetime import datetime
from analise import Analise
from config import Config


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
    if df.empty:
        flash('O arquivo CSV está vazio', 'error')
        return redirect(url_for('csv_list', id_usuario=id_usuario))
    page = request.args.get('page', default=1, type=int)
    per_page = 5
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    data = df.iloc[start_idx:end_idx]
    num_pages = len(df) // per_page + 1
    return render_template('dashboard.html', id_usuario=id_usuario,id=id,data=data, 
                           page=page, num_pages=num_pages)

## Analise ##
@app.route('/analise/<int:id_usuario>/<int:id>', methods=['GET'])
def analise(id_usuario,id):
    df = instancia.ler_ultimo_arquivo(id)
    situacao_aluno = instancia.mostrar_grafico_situacao_aluno(df)
    filtro_ano = request.args.get('filtro_ano')
    maior_reprovacao= instancia.filtro_reprovacao(df,filtro_ano)
    maior_reprovacao_html=maior_reprovacao.to_html(classes='table table-striped')
    comp= instancia.mostrar_grafico_comparativo(df)
    formandos= instancia.analise_formandos(df)
    formandos_html = formandos.to_html(classes='table table-striped')
    analise_formando= instancia.analise_estatistica_formado(df)
    analise_formando_html= analise_formando.to_html(classes='table table-strip')
    page=1
    cont_page=10
    data=df
    filtro = request.args.get('filtro')
    busca_aluno= instancia.filtro_alunos(df,filtro,id,page,cont_page)
    analise_cotista = instancia.analise_estatistica_formado_cotista(df).to_html(classes='table table-strip')
    analise_n_cotista = instancia.analise_estatistica_formado_n_cotista(df).to_html(classes='table table-strip')
    analise_outro = instancia.analise_estatistica_formado_outros(df).to_html(classes='table table-strip')
    return render_template('analise.html', id_usuario=id_usuario,id=id,page=page,
                           plot=situacao_aluno.to_html(full_html=False), 
                           maior_reprovacao=maior_reprovacao_html,
                           comparativo=comp, data=data, formandos=formandos_html,
                           analise_form=analise_formando_html,
                           busca_aluno=busca_aluno, analise_n_cotista=analise_n_cotista,
                           analise_cotista=analise_cotista, analise_outro=analise_outro
                           )


if __name__ == '__main__':
    app.run(debug=True)


