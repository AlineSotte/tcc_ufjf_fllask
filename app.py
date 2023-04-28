from flask import Flask, render_template, request, redirect, url_for,session
from flask_bootstrap import Bootstrap
from datetime import datetime
import mysql.connector
from config import Config
from analise import *
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.offline as pyo



app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
bootstrap = Bootstrap(app)
app.config['SESSION_TYPE'] = Config.SESSION_TYPE
app.config['SESSION_FILE_DIR'] = Config.SESSION_FILE_DIR


# Criando uma conexão com o banco de dados MySQL
connection = mysql.connector.connect(
    host=Config.HOST,
    user=Config.USER,
    password=Config.PASSWORD,
    db=Config.DB,
)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    cursor = connection.cursor()
    username = request.form['username']
    password = request.form['password']
    cursor.execute('SELECT id FROM usuarios WHERE email = %s AND senha = %s', (username, password))
    id_usuario = cursor.fetchone()
    if id_usuario is None:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('csv', id_usuario=id_usuario[0]))

@app.route('/csv/<int:id_usuario>', methods=['GET', 'POST'])
def csv(id_usuario):
    agora = datetime.now()
    data_hora = agora.strftime("%d%m%Y%H%M%S")
    
    if request.method == 'POST':
        arquivo = request.files['arquivo_csv']
        arquivo_bytes = arquivo.read()
        nome_arq= f'arquivo_{data_hora}'
        cursor = connection.cursor()
        cursor.execute("INSERT INTO tabela_csv (id_usuario, arquivo_csv,nome_arquivo) VALUES (%s, %s,%s)", (id_usuario, arquivo_bytes,nome_arq))
        connection.commit()
        cursor.close()
        return render_template('dashboard', id_usuario=id_usuario)
    else:
        return render_template('csv.html', id_usuario=id_usuario)


@app.route('/dashboard/<int:id_usuario>', methods=['GET'])
def dashboard(id_usuario):
    df = pd.read_csv('/home/aline/Documentos/flask_tcc_si/si_ultimo_dado.csv', encoding='utf8', sep=';')
    df.head()
    page = request.args.get('page', default=1, type=int)
    per_page = 10
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    data = df.iloc[start_idx:end_idx]
    num_pages = len(df) // per_page + 1
    return render_template('dashboard.html', id_usuario=id_usuario,data=data, page=page, num_pages=num_pages)

    
## Funcoes Analise ##

def mostrar_grafico_situacao_aluno():
    arquivo_csv= pd.read_csv('/home/aline/Documentos/flask_tcc_si/si_ultimo_dado.csv', encoding='utf8', sep=';')
    df2 = pd.DataFrame(arquivo_csv, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DATACOLACAO','DATAENCERRAMENTO','IRA','CURRICULO','CARGA_HOR'])
    dados_unicos = df2.drop_duplicates().reset_index(drop=True)

    agrupamento_dados = dados_unicos.groupby(['SITUACAO_ALUNO']).size()\
    .sort_values(ascending=False) \
    .reset_index(name='TOTAL_SITUACAO_ALUNO') 

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Bar(x=agrupamento_dados['SITUACAO_ALUNO'], y=agrupamento_dados['TOTAL_SITUACAO_ALUNO']), row=1, col=1)
    fig.update_layout(title='Contagem da Situação dos Alunos', xaxis_title='Situação Aluno', yaxis_title='Total por Situação dos Alunos')

    return fig
  

def mostrar_grafico_comparativo():
    arquivo_csv= pd.read_csv('/home/aline/Documentos/flask_tcc_si/si_ultimo_dado.csv', encoding='utf8', sep=';')

    df2 = pd.DataFrame(arquivo_csv, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DATACOLACAO','DATAENCERRAMENTO','IRA','CURRICULO','CARGA_HOR'])
    dados_unicos = df2.drop_duplicates().reset_index(drop=True)

    dado_n_cota = dados_unicos.query('TIPOINGRESSO in ("SISU - GRUPO C","SISU - GRUPO C VG Edital","SISU - grupo C - mudança de curso","PISM C/Mudança de Curso","PISM C")').groupby(['SITUACAO_ALUNO']).size()\
    .sort_values(ascending=False) \
    .reset_index(name='TOTAL') 
    dado_n_cota ['Tipo'] = pd.Series(['N_Cota' for x in range(len(dado_n_cota.index))])

    dado_outros = dados_unicos.query('TIPOINGRESSO in ("Sentença Judicial","Transferęncia Obrigatória","Vestibular","CV/Mudança de Curso","Programa de Ingresso Seletivo Misto")').groupby(['SITUACAO_ALUNO']).size()\
    .sort_values(ascending=False) \
    .reset_index(name='TOTAL') 
    dado_outros['Tipo'] = pd.Series(['Outros' for x in range(len(dado_outros.index))])

    dado_cota = dados_unicos.query('TIPOINGRESSO not in ("SISU - GRUPO C","SISU - GRUPO C VG Edital","SISU - grupo C - mudança de curso","PISM C/Mudança de Curso","PISM C","Sentença Judicial","Transferęncia Obrigatória","Vestibular","CV/Mudança de Curso","Programa de Ingresso Seletivo Misto")').groupby(['SITUACAO_ALUNO']).size()\
    .sort_values(ascending=False) \
    .reset_index(name='TOTAL') 
    dado_cota['Tipo'] = pd.Series(['Cota' for x in range(len(dado_cota.index))])

    uniao_analise=pd.concat([dado_n_cota,dado_cota,dado_outros])

    print(uniao_analise)

    uniao_analise.plot.bar(color='royalblue', ec='k', alpha=0.6)
    plt.xticks(rotation=90, fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlabel('situacao aluno')
    plt.ylabel('total')


def mostrar_grafico_comparativo():
    arquivo_csv= pd.read_csv('/home/aline/Documentos/flask_tcc_si/si_ultimo_dado.csv', encoding='utf8', sep=';')

    df2 = pd.DataFrame(arquivo_csv, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DATACOLACAO','DATAENCERRAMENTO','IRA','CURRICULO','CARGA_HOR'])
    dados_unicos = df2.drop_duplicates().reset_index(drop=True)

    dado_n_cota = dados_unicos.query('TIPOINGRESSO in ("SISU - GRUPO C","SISU - GRUPO C VG Edital","SISU - grupo C - mudança de curso","PISM C/Mudança de Curso","PISM C")').groupby(['SITUACAO_ALUNO']).size()\
    .sort_values(ascending=False) \
    .reset_index(name='TOTAL') 
    dado_n_cota ['Tipo'] = pd.Series(['N_Cota' for x in range(len(dado_n_cota.index))])

    dado_outros = dados_unicos.query('TIPOINGRESSO in ("Sentença Judicial","Transferęncia Obrigatória","Vestibular","CV/Mudança de Curso","Programa de Ingresso Seletivo Misto")').groupby(['SITUACAO_ALUNO']).size()\
    .sort_values(ascending=False) \
    .reset_index(name='TOTAL') 
    dado_outros['Tipo'] = pd.Series(['Outros' for x in range(len(dado_outros.index))])

    dado_cota = dados_unicos.query('TIPOINGRESSO not in ("SISU - GRUPO C","SISU - GRUPO C VG Edital","SISU - grupo C - mudança de curso","PISM C/Mudança de Curso","PISM C","Sentença Judicial","Transferęncia Obrigatória","Vestibular","CV/Mudança de Curso","Programa de Ingresso Seletivo Misto")').groupby(['SITUACAO_ALUNO']).size()\
    .sort_values(ascending=False) \
    .reset_index(name='TOTAL') 

    dado_cota['Tipo'] = pd.Series(['Cota' for x in range(len(dado_cota.index))])
    df=pd.concat([dado_n_cota,dado_cota,dado_outros])
    
    trace1 = go.Bar(x=df[(df['Tipo'] == 'Cota')]['SITUACAO_ALUNO'], y=df[(df['Tipo'] == 'Cota')]['TOTAL'],
                    name='Cota', marker=dict(color='#2ecc71'))
    trace2 = go.Bar(x=df[(df['Tipo'] == 'N_Cota')]['SITUACAO_ALUNO'], y=df[(df['Tipo'] == 'N_Cota')]['TOTAL'],
                    name='Não Cota', marker=dict(color='#3498db'))
    trace3 = go.Bar(x=df[(df['Tipo'] == 'Outros')]['SITUACAO_ALUNO'], y=df[(df['Tipo'] == 'Outros')]['TOTAL'],
                    name='Outros', marker=dict(color='#e74c3c'))
    data = [trace1, trace2, trace3]
    layout = go.Layout(title='Gráfico Interativo com Três Variáveis',
                       xaxis=dict(title='Situação do Aluno'),
                       yaxis=dict(title='Total'),
                       barmode='group')
    fig = go.Figure(data=data, layout=layout)

    # Renderiza o gráfico no HTML usando a função 'plot' do Plotly
    plot_div = fig.to_html(full_html=False)
    
    return plot_div

  
def calcular_diciplinas_maior_reprovacao():
    arquivo_csv= pd.read_csv('/home/aline/Documentos/flask_tcc_si/si_ultimo_dado.csv', encoding='utf8', sep=';')
    df_rep= pd.DataFrame(arquivo_csv, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DISCIPLINA','PERIODO', 'NOTA','SITUACAO_DISCIPLINA'])
    reprovacao_disciplina= df_rep.query('SITUACAO_DISCIPLINA in ("Reprovado","Rep Nota")')
    agrupamento_dados_rep = reprovacao_disciplina.groupby(['DISCIPLINA']).size()\
        .sort_values(ascending=False) \
        .reset_index(name='TOTAL_REPROVACAO') 
    return agrupamento_dados_rep.nlargest(n=10, columns=['TOTAL_REPROVACAO'])
  
  
@app.route('/analise/<int:id_usuario>', methods=['GET'])
def analise(id_usuario):
    situacao_aluno = mostrar_grafico_situacao_aluno()
    maior_reprovacao= calcular_diciplinas_maior_reprovacao()
    comp= mostrar_grafico_comparativo()
    return render_template('analise.html', id_usuario=id_usuario,plot=situacao_aluno.to_html(full_html=False), maior_reprovacao=maior_reprovacao.to_html(classes='table table-striped'), comparativo=comp)
  
if __name__ == '__main__':
    app.run(debug=Config.DEBUG)


