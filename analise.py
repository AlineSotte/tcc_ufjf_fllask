from plotly.subplots import make_subplots
from models import db, Usuario, Arquivo
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

        uniao_analise=pd.concat([dado_n_cota,dado_cota,dado_outros])
        
        uniao_analise.plot.bar(color='royalblue', ec='k', alpha=0.6)
        plt.xticks(rotation=90, fontsize=12)
        plt.yticks(fontsize=12)
        plt.xlabel('situacao aluno')
        plt.ylabel('total')


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
        df = pd.read_csv(io.StringIO(dados_csv))
        return df
    
    def pegar_id(self,arquivo):
        arq = Arquivo.query.filter_by(nome_arquivo=arquivo).first()
        return arq.id
    
    