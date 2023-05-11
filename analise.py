from plotly.subplots import make_subplots
from models import Arquivo
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import pandas as pd
import io


class Analise:
    
    def mostrar_grafico_situacao_aluno(self,arquivo):
        arquivo_csv= arquivo
        df2 = pd.DataFrame(arquivo_csv, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DATACOLACAO','DATAENCERRAMENTO','IRA','CURRICULO','CARGA_HOR'])
        dados_unicos = df2.drop_duplicates().reset_index(drop=True)

        agrupamento_dados = dados_unicos.groupby(['SITUACAO_ALUNO']).size()\
        .sort_values(ascending=False) \
        .reset_index(name='TOTAL_SITUACAO_ALUNO') 

        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Bar(x=agrupamento_dados['SITUACAO_ALUNO'], y=agrupamento_dados['TOTAL_SITUACAO_ALUNO']), row=1, col=1)
        fig.update_layout(title='Contagem da Situação dos Alunos', xaxis_title='Situação Aluno', yaxis_title='Total por Situação dos Alunos')

        return fig

    def mostrar_grafico_comparativo(self,arquivo):
        arquivo_csv= arquivo

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
                        name='Cotista', marker=dict(color='#2ecc71'))
        trace2 = go.Bar(x=df[(df['Tipo'] == 'N_Cota')]['SITUACAO_ALUNO'], y=df[(df['Tipo'] == 'N_Cota')]['TOTAL'],
                        name='Não Cotista', marker=dict(color='#3498db'))
        trace3 = go.Bar(x=df[(df['Tipo'] == 'Outros')]['SITUACAO_ALUNO'], y=df[(df['Tipo'] == 'Outros')]['TOTAL'],
                        name='Outros', marker=dict(color='#e74c3c'))
        data = [trace1, trace2, trace3]
        layout = go.Layout(title='Gráfico Comparativos em relação ao Ingresso na UFJF',
                        xaxis=dict(title='Situação do Aluno'),
                        yaxis=dict(title='Total'),
                        barmode='group')
        fig = go.Figure(data=data, layout=layout)
        plot_div = fig.to_html(full_html=False)
        
        return plot_div


    def calcular_diciplinas_maior_reprovacao(self,arquivo):
        arquivo_csv= arquivo
        df_rep= pd.DataFrame(arquivo_csv, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DISCIPLINA','PERIODO', 'NOTA','SITUACAO_DISCIPLINA'])
        reprovacao_disciplina= df_rep.query('SITUACAO_DISCIPLINA in ("Reprovado","Rep Nota")')
        agrupamento_dados_rep = reprovacao_disciplina.groupby(['DISCIPLINA']).size()\
            .sort_values(ascending=False) \
            .reset_index(name='TOTAL_REPROVACAO') 
        return agrupamento_dados_rep.nlargest(n=10, columns=['TOTAL_REPROVACAO'])
        
    def ler_ultimo_arquivo(self,id):
        arquivo = Arquivo.query.filter_by(id=id).first()
        dados_csv = arquivo.arquivo_csv.decode('utf-8')
        df = pd.read_csv(io.StringIO(dados_csv),sep="[,;]", decimal=',')
        return df
    
    def pegar_id(self,arquivo):
        arq = Arquivo.query.filter_by(nome_arquivo=arquivo).first()
        return arq.id
    
    def listar_cinco_arquivos(self, id_usuario):
        arquivos = Arquivo.query.filter_by(usuario_id=id_usuario).filter(Arquivo.nome_arquivo != 'template_analise_2023_05_07_20_53_40').order_by(Arquivo.id.desc()).limit(5).all()
        return arquivos

    def analise_formandos(self,arquivo):
        df_rep = pd.DataFrame(arquivo, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DATACOLACAO','IRA'])
        df = df_rep.dropna(subset=['DATACOLACAO'])
        ano_formado = df.DATACOLACAO
        ano_final = ano_formado.astype(str).apply(lambda x: x.split('/')[2])
        df.insert(3, "AnoSaida",ano_final, True)
        dados_unicos = df.drop_duplicates().reset_index(drop=True)
        form= dados_unicos[['AnoSaida', 'ALUNO']]
        formandos = form.groupby(['AnoSaida']).size().to_frame().reset_index()
        formandos = formandos.rename(columns={'AnoSaida': 'Ano', 0: 'Formandos'})
        return formandos

    def analise_estatistica_formado(self,arquivo):
        df_rep= pd.DataFrame(arquivo, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DATACOLACAO','IRA'])
        df= df_rep.dropna(subset=['DATACOLACAO'])
        df.head()
        ano_semestre = df.INGRESSO
        ano = ano_semestre.astype(str).apply(lambda x: x.split('/')[0])
        ano_formado = df.DATACOLACAO
        ano_final = ano_formado.astype(str).apply(lambda x: x.split('/')[2])
        tempo_formar = ano_final.astype(int) - ano.astype(int)
        df.insert(2, "AnoEntrada",ano, True)
        df.insert(3, "AnoSaida",ano_final, True)
        df.insert(4, "Tempo de Graduação",tempo_formar, True)
        dados_unicos = df.drop_duplicates().reset_index(drop=True)
        data = dados_unicos[['Tempo de Graduação', 'IRA']]
        descricao = data.describe().T
        descricao = descricao.rename(columns={
                'count': 'Total',
                'mean': 'Média',
                'std': 'Desvio Padrão',
                'min': 'Mínimo',
                '25%': '1º Quartil',
                '50%': 'Mediana',
                '75%': '3º Quartil',
                'max': 'Máximo'
            })
        descricao = descricao.round(1)
        return descricao

    def analise_estatistica_formado_n_cotista(self,arquivo):
        df_rep= pd.DataFrame(arquivo, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DATACOLACAO','IRA'])
        df= df_rep.dropna(subset=['DATACOLACAO'])
        df.head()
        ano_semestre = df.INGRESSO
        ano = ano_semestre.astype(str).apply(lambda x: x.split('/')[0])
        ano_formado = df.DATACOLACAO
        ano_final = ano_formado.astype(str).apply(lambda x: x.split('/')[2])
        tempo_formar = ano_final.astype(int) - ano.astype(int)
        df.insert(2, "AnoEntrada",ano, True)
        df.insert(3, "AnoSaida",ano_final, True)
        df.insert(4, "Tempo de Graduação",tempo_formar, True)
        dados_unicos = df.drop_duplicates().reset_index(drop=True)
        dado_n_cota = dados_unicos.query('TIPOINGRESSO in ("SISU - GRUPO C","SISU - GRUPO C VG Edital","SISU - grupo C - mudança de curso","PISM C/Mudança de Curso","PISM C")')
        data = dado_n_cota[['Tempo de Graduação', 'IRA']]
        descricao = data.describe().T
        descricao = descricao.rename(columns={
                'count': 'Total',
                'mean': 'Média',
                'std': 'Desvio Padrão',
                'min': 'Mínimo',
                '25%': '1º Quartil',
                '50%': 'Mediana',
                '75%': '3º Quartil',
                'max': 'Máximo'
            })
        descricao = descricao.round(1)
        return descricao
    
    def analise_estatistica_formado_cotista(self,arquivo):
        df_rep= pd.DataFrame(arquivo, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DATACOLACAO','IRA'])
        df= df_rep.dropna(subset=['DATACOLACAO'])
        df.head()
        ano_semestre = df.INGRESSO
        ano = ano_semestre.astype(str).apply(lambda x: x.split('/')[0])
        ano_formado = df.DATACOLACAO
        ano_final = ano_formado.astype(str).apply(lambda x: x.split('/')[2])
        tempo_formar = ano_final.astype(int) - ano.astype(int)
        df.insert(2, "AnoEntrada",ano, True)
        df.insert(3, "AnoSaida",ano_final, True)
        df.insert(4, "Tempo de Graduação",tempo_formar, True)
        dados_unicos = df.drop_duplicates().reset_index(drop=True)
        dado_cota = dados_unicos.query('TIPOINGRESSO not in ("SISU - GRUPO C","SISU - GRUPO C VG Edital","SISU - grupo C - mudança de curso","PISM C/Mudança de Curso","PISM C","Sentença Judicial","Transferęncia Obrigatória","Vestibular","CV/Mudança de Curso","Programa de Ingresso Seletivo Misto")')
        teste = dado_cota[['Tempo de Graduação', 'IRA']]
        descricao = teste.describe().T
        descricao = descricao.rename(columns={
                'count': 'Total',
                'mean': 'Média',
                'std': 'Desvio Padrão',
                'min': 'Mínimo',
                '25%': '1º Quartil',
                '50%': 'Mediana',
                '75%': '3º Quartil',
                'max': 'Máximo'
            })
        descricao = descricao.round(1)
        return descricao

    def analise_estatistica_formado_outros(self,arquivo):
        df_rep= pd.DataFrame(arquivo, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DATACOLACAO','IRA'])
        df= df_rep.dropna(subset=['DATACOLACAO'])
        df.head()
        ano_semestre = df.INGRESSO
        ano = ano_semestre.astype(str).apply(lambda x: x.split('/')[0])
        ano_formado = df.DATACOLACAO
        ano_final = ano_formado.astype(str).apply(lambda x: x.split('/')[2])
        tempo_formar = ano_final.astype(int) - ano.astype(int)
        df.insert(2, "AnoEntrada",ano, True)
        df.insert(3, "AnoSaida",ano_final, True)
        df.insert(4, "Tempo de Graduação",tempo_formar, True)
        dados_unicos = df.drop_duplicates().reset_index(drop=True)
        dado_outros = dados_unicos.query('TIPOINGRESSO in ("Sentença Judicial","Transferęncia Obrigatória","Vestibular","CV/Mudança de Curso","Programa de Ingresso Seletivo Misto")')
        data= dado_outros[['Tempo de Graduação', 'IRA']]
        descricao = data.describe().T
        descricao = descricao.rename(columns={
                'count': 'Total',
                'mean': 'Média',
                'std': 'Desvio Padrão',
                'min': 'Mínimo',
                '25%': '1º Quartil',
                '50%': 'Mediana',
                '75%': '3º Quartil',
                'max': 'Máximo'
            })
        descricao = descricao.round(1)
        return descricao

    def alunos_curso(self,arquivo, pagina, linhas_por_pagina):
        df2 = pd.DataFrame(arquivo, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DATACOLACAO','DATAENCERRAMENTO','IRA','CARGA_HOR'])
        dados_unicos = df2.drop_duplicates().reset_index(drop=True)
        inicio = (pagina - 1) * linhas_por_pagina
        fim = inicio + linhas_por_pagina
        dados_paginados = dados_unicos.iloc[inicio:fim]
        return dados_paginados
    
    def pegar_aluno(self,id_arquivo,nome_aluno):
        arquivo = self.ler_ultimo_arquivo(id_arquivo)
        if arquivo['ALUNO'].dtype != 'object':
            arquivo['ALUNO'] = arquivo['ALUNO'].astype(str)
        busca_arquivo = arquivo.loc[arquivo['ALUNO'].str.contains(nome_aluno)]
        cont_alunos = busca_arquivo.shape[0]
        aplica_paginacao = self.alunos_curso(busca_arquivo, 1, cont_alunos)
        return aplica_paginacao
    
    def filtro_alunos(self,arquivo,filtro,id,page,cont_page):
        if filtro != None:
            busca_aluno = self.pegar_aluno(id,filtro)
            return busca_aluno
        else:
            alunos = self.alunos_curso(arquivo,page,cont_page)
            return alunos