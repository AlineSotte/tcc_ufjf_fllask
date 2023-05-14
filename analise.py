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
    
    def ler_ultimo_arquivo(self,id):
        arquivo = Arquivo.query.filter_by(id=id).first()
        dados_csv = arquivo.arquivo_csv.decode('utf-8')
        df = pd.read_csv(io.StringIO(dados_csv),sep="[,;]", decimal=',')
        return df
    
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
        df_rep= pd.DataFrame(arquivo, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DISCIPLINA','PERIODO', 'NOTA','SITUACAO_DISCIPLINA'])
        reprovacao_disciplina= df_rep.query('SITUACAO_DISCIPLINA in ("Reprovado","Rep Nota")')
        agrupamento_dados_rep = reprovacao_disciplina.groupby(['DISCIPLINA']).size()\
            .sort_values(ascending=False) \
            .reset_index(name='TOTAL_REPROVACAO') 
        return agrupamento_dados_rep.nlargest(n=10, columns=['TOTAL_REPROVACAO'])
    
    def calcular_diciplinas_maior_reprovacao_ano(self,arquivo,ano,situacao):
        
        df_rep= pd.DataFrame(arquivo, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DISCIPLINA','PERIODO', 'NOTA','SITUACAO_DISCIPLINA'])
        reprovacao_disciplina= df_rep.query('SITUACAO_DISCIPLINA in ("Reprovado","Rep Nota")')
        
        ano_semestre = reprovacao_disciplina.PERIODO
        ano_materia = ano_semestre.astype(str).apply(lambda x: x.split('/')[0])
        reprovacao_disciplina.insert(reprovacao_disciplina.shape[1]-1, "AnoDisciplina",ano_materia,True)
        reprovacao_disciplina['AnoDisciplina'] = reprovacao_disciplina['AnoDisciplina'].astype(str)
         
        if ano != '' and situacao == '':
            busca_ano = reprovacao_disciplina[reprovacao_disciplina['AnoDisciplina'].str.contains(ano)].reset_index(drop=True)
            agrupamento_dados_rep = busca_ano.groupby(['DISCIPLINA']).size()\
                .sort_values(ascending=False) \
                .reset_index(name='TOTAL_REPROVACAO') 
            return agrupamento_dados_rep.nlargest(n=10, columns=['TOTAL_REPROVACAO'])
        
        elif ano == '' and situacao != '':
            if situacao == 'cotista':
                dado_cota = reprovacao_disciplina.query('TIPOINGRESSO not in ("SISU - GRUPO C","SISU - GRUPO C VG Edital","SISU - grupo C - mudança de curso","PISM C/Mudança de Curso","PISM C","Sentença Judicial","Transferęncia Obrigatória","Vestibular","CV/Mudança de Curso","Programa de Ingresso Seletivo Misto")').groupby('DISCIPLINA').size()\
                    .sort_values(ascending=False) \
                    .reset_index(name='TOTAL_REPROVACAO') 
                return dado_cota.nlargest(n=10, columns=['TOTAL_REPROVACAO'])
            
            elif situacao == 'nao-cotista':
                dado_n_cota = reprovacao_disciplina.query('TIPOINGRESSO in ("SISU - GRUPO C","SISU - GRUPO C VG Edital","SISU - grupo C - mudança de curso","PISM C/Mudança de Curso","PISM C")').groupby(['DISCIPLINA']).size()\
                    .sort_values(ascending=False) \
                    .reset_index(name='TOTAL_REPROVACAO') 
                return dado_n_cota.nlargest(n=10, columns=['TOTAL_REPROVACAO'])
            else:
                dado_outros = reprovacao_disciplina.query('TIPOINGRESSO in ("Sentença Judicial","Transferęncia Obrigatória","Vestibular","CV/Mudança de Curso","Programa de Ingresso Seletivo Misto")').groupby(['DISCIPLINA']).size()\
                    .sort_values(ascending=False) \
                    .reset_index(name='TOTAL_REPROVACAO') 
                return dado_outros.nlargest(n=10, columns=['TOTAL_REPROVACAO'])
        else:
            busca_ano = reprovacao_disciplina[reprovacao_disciplina['AnoDisciplina'].str.contains(ano)].reset_index(drop=True)
            if situacao == 'cotista':
                agrupamento_dados_rep = busca_ano.query('TIPOINGRESSO not in ("SISU - GRUPO C","SISU - GRUPO C VG Edital","SISU - grupo C - mudança de curso","PISM C/Mudança de Curso","PISM C","Sentença Judicial","Transferęncia Obrigatória","Vestibular","CV/Mudança de Curso","Programa de Ingresso Seletivo Misto")').groupby(['DISCIPLINA']).size()\
                .sort_values(ascending=False) \
                .reset_index(name='TOTAL_REPROVACAO') 
                return agrupamento_dados_rep.nlargest(n=10, columns=['TOTAL_REPROVACAO'])
            elif situacao == 'nao-cotista':
                agrupamento_dados_rep = busca_ano.query('TIPOINGRESSO in ("SISU - GRUPO C","SISU - GRUPO C VG Edital","SISU - grupo C - mudança de curso","PISM C/Mudança de Curso","PISM C")').groupby(['DISCIPLINA']).size()\
                .sort_values(ascending=False) \
                .reset_index(name='TOTAL_REPROVACAO') 
                return agrupamento_dados_rep.nlargest(n=10, columns=['TOTAL_REPROVACAO'])
            else:
                agrupamento_dados_rep = busca_ano.query('TIPOINGRESSO in ("Sentença Judicial","Transferęncia Obrigatória","Vestibular","CV/Mudança de Curso","Programa de Ingresso Seletivo Misto")').groupby(['DISCIPLINA']).size()\
                .sort_values(ascending=False) \
                .reset_index(name='TOTAL_REPROVACAO') 
                return agrupamento_dados_rep.nlargest(n=10, columns=['TOTAL_REPROVACAO'])
         
    def filtro_reprovacao(self,arquivo,filtro,situacao):
        if filtro!= '' or situacao != '':
            rep_ano = self.calcular_diciplinas_maior_reprovacao_ano(arquivo,filtro,situacao)
            return rep_ano
        else:
            alunos = self.calcular_diciplinas_maior_reprovacao(arquivo)
            return alunos
        
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
    
    def analise_estatistica(self,arquivo):
        df_rep= pd.DataFrame(arquivo, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DATACOLACAO','IRA'])
        df= df_rep.dropna(subset=['DATACOLACAO'])
        ano_semestre = df.INGRESSO
        ano = ano_semestre.astype(str).apply(lambda x: x.split('/')[0])
        ano_formado = df.DATACOLACAO
        ano_final = ano_formado.astype(str).apply(lambda x: x.split('/')[2])
        tempo_formar = ano_final.astype(int) - ano.astype(int)
        df.insert(2, "AnoEntrada",ano, True)
        df.insert(3, "AnoSaida",ano_final, True)
        df.insert(4, "Tempo de Graduação",tempo_formar, True)
        dados_unicos = df.drop_duplicates().reset_index(drop=True)
        return dados_unicos
    
    def metrica_estatistica(self,arquivo):
        descricao = arquivo.describe().T
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
    
    def analise_estatistica_formando(self,arquivo):
        dado_unico = self.analise_estatistica(arquivo)
        data = dado_unico[['Tempo de Graduação', 'IRA']]
        analise_formando = self.metrica_estatistica(data)
        return analise_formando

    def analise_estatistica_formando_n_cotista(self,arquivo):
        dados_unicos = self.analise_estatistica(arquivo)
        dado_n_cota = dados_unicos.query('TIPOINGRESSO in ("SISU - GRUPO C","SISU - GRUPO C VG Edital","SISU - grupo C - mudança de curso","PISM C/Mudança de Curso","PISM C")')
        data = dado_n_cota[['Tempo de Graduação', 'IRA']]
        descricao=self.metrica_estatistica(data)
        return descricao
    
    def analise_estatistica_formando_cotista(self,arquivo):
        dados_unicos = self.analise_estatistica(arquivo)
        dado_cota = dados_unicos.query('TIPOINGRESSO not in ("SISU - GRUPO C","SISU - GRUPO C VG Edital","SISU - grupo C - mudança de curso","PISM C/Mudança de Curso","PISM C","Sentença Judicial","Transferęncia Obrigatória","Vestibular","CV/Mudança de Curso","Programa de Ingresso Seletivo Misto")')
        data = dado_cota[['Tempo de Graduação', 'IRA']]
        descricao = self.metrica_estatistica(data)
        return descricao

    def analise_estatistica_formando_outros(self,arquivo):
        dados_unicos = self.analise_estatistica(arquivo)
        dado_outros = dados_unicos.query('TIPOINGRESSO in ("Sentença Judicial","Transferęncia Obrigatória","Vestibular","CV/Mudança de Curso","Programa de Ingresso Seletivo Misto")')
        data= dado_outros[['Tempo de Graduação', 'IRA']]
        descricao = self.metrica_estatistica(data)
        return descricao

    def alunos_curso(self,arquivo):
        df2 = pd.DataFrame(arquivo, columns=['INGRESSO','ALUNO','TIPOINGRESSO','SITUACAO_ALUNO','DATACOLACAO','DATAENCERRAMENTO','IRA','CARGA_HOR'])
        dados_unicos = df2.drop_duplicates().reset_index(drop=True)
        return dados_unicos
    
    def pegar_aluno(self,arquivo,nome_aluno,situacao_aluno):
        if arquivo['ALUNO'].dtype != 'object':
            arquivo['ALUNO'] = arquivo['ALUNO'].astype(str)
        if nome_aluno != '' and situacao_aluno == '':
            busca_arquivo =  arquivo[arquivo['ALUNO'].str.contains(nome_aluno)].reset_index(drop=True)
            cont_alunos = busca_arquivo.shape[0]
            return  self.alunos_curso(busca_arquivo)
        elif nome_aluno == '' and situacao_aluno !='':
            if situacao_aluno == 'ativo':
                arquivo_situacao = arquivo[arquivo['SITUACAO_ALUNO'] == 'Ativo']
                return  self.alunos_curso(arquivo_situacao)
            elif situacao_aluno == 'trancado':
                arquivo_situacao = arquivo[arquivo['SITUACAO_ALUNO'] == 'Trancado']
                return  self.alunos_curso(arquivo_situacao)
            elif situacao_aluno == 'cancelado':
                arquivo_situacao = arquivo[arquivo['SITUACAO_ALUNO'] == 'Cancelado']
                return  self.alunos_curso(arquivo_situacao)
            elif situacao_aluno == 'jubilado':
                arquivo_situacao = arquivo[arquivo['SITUACAO_ALUNO'] == 'Jubilado']
                return  self.alunos_curso(arquivo_situacao)
            elif situacao_aluno == 'concluido':
                arquivo_situacao = arquivo[arquivo['SITUACAO_ALUNO'] == 'Concluido']
                return  self.alunos_curso(arquivo_situacao)
            elif situacao_aluno == 'transferido':
                arquivo_situacao = arquivo[arquivo['SITUACAO_ALUNO'] == 'Transferido']
                return  self.alunos_curso(arquivo_situacao)
            else:
                arquivo_situacao = arquivo[arquivo['SITUACAO_ALUNO'] == 'Suspensăo']
                return  self.alunos_curso(arquivo_situacao)
        else: 
            busca_arquivo =  arquivo[arquivo['ALUNO'].str.contains(nome_aluno)].reset_index(drop=True)
            if situacao_aluno == 'ativo':
                arquivo_situacao = busca_arquivo[busca_arquivo['SITUACAO_ALUNO'] == 'Ativo']
                return  self.alunos_curso(arquivo_situacao)
            elif situacao_aluno == 'trancado':
                arquivo_situacao = busca_arquivo[busca_arquivo['SITUACAO_ALUNO'] == 'Trancado']
                return  self.alunos_curso(arquivo_situacao)
            elif situacao_aluno == 'cancelado':
                arquivo_situacao = busca_arquivo[busca_arquivo['SITUACAO_ALUNO'] == 'Cancelado']
                return  self.alunos_curso(arquivo_situacao)
            elif situacao_aluno == 'jubilado':
                arquivo_situacao = busca_arquivo[busca_arquivo['SITUACAO_ALUNO'] == 'Jubilado']
                return  self.alunos_curso(arquivo_situacao)
            elif situacao_aluno == 'concluido':
                arquivo_situacao = busca_arquivo[busca_arquivo['SITUACAO_ALUNO'] == 'Concluido']
                return  self.alunos_curso(arquivo_situacao)
            elif situacao_aluno == 'transferido':
                arquivo_situacao = busca_arquivo[busca_arquivo['SITUACAO_ALUNO'] == 'Transferido']
                return  self.alunos_curso(arquivo_situacao)
            else:
                arquivo_situacao = busca_arquivo[busca_arquivo['SITUACAO_ALUNO'] == 'Suspensăo']
                return  self.alunos_curso(arquivo_situacao)
            
    def filtro_alunos(self,arquivo,filtro,situacao_aluno):
        if filtro != '' or situacao_aluno != '':
            busca_aluno = self.pegar_aluno(arquivo,filtro,situacao_aluno)
            return busca_aluno
        else:
            alunos = self.alunos_curso(arquivo)
            return alunos