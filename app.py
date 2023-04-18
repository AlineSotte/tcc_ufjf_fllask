from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import mysql.connector
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY


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
    data_hora = agora.strftime("%d%m%Y%_H%M%S")
    
    if request.method == 'POST':
        arquivo = request.files['arquivo_csv']
        arquivo_bytes = arquivo.read()
        nome_arq= f'arquivo_{data_hora}'
        cursor = connection.cursor()
        cursor.execute("INSERT INTO tabela_csv (id_usuario, arquivo_csv,nome_arquivo) VALUES (%s, %s,%s)", (id_usuario, arquivo_bytes,nome_arq))
        connection.commit()
        cursor.close()
        return 'Arquivo CSV enviado com sucesso'
    else:
        return render_template('csv.html', id_usuario=id_usuario)

if __name__ == '__main__':
    app.run(Config.DEBUG)


