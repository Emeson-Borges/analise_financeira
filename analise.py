import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Função para ler o arquivo carregado e retornar um DataFrame
def carregar_arquivo(uploaded_file):
    if uploaded_file is not None:
        extensao = uploaded_file.name.split(".")[-1].lower()
        if extensao == 'csv':
            return pd.read_csv(uploaded_file)
        elif extensao in ['xls', 'xlsx']:
            return pd.read_excel(uploaded_file)
        elif extensao == 'txt':
            return pd.read_csv(uploaded_file, sep='\t')
        else:
            st.error('Formato de arquivo não suportado. Por favor, selecione um arquivo CSV, Excel ou TXT.')

# Função para gerar relatório
def gerar_relatorio(titulo, imagens, dados):
    st.header(titulo)
    
    for imagem in imagens:
        st.image(imagem, caption='', use_column_width=True)

    st.subheader('Dados dos Meses')
    st.write(dados)

# Título da aplicação
st.title('Análise Financeira')

# Upload do arquivo
st.sidebar.title('Upload do Arquivo')
uploaded_file = st.sidebar.file_uploader('Selecione um arquivo CSV, Excel ou TXT:', type=['csv', 'xls', 'xlsx', 'txt'])

# Verificar se um arquivo foi carregado
if uploaded_file is not None:
    # Carregar os dados financeiros
    dados_financeiros = carregar_arquivo(uploaded_file)

    if dados_financeiros is not None:
        # Sidebar para seleção de filtros
        st.sidebar.title('Filtros')
        categorias = st.sidebar.multiselect('Selecione as Categorias:', dados_financeiros.columns[1:])

        # Verificar se pelo menos uma categoria foi selecionada
        if not categorias:
            st.warning('Por favor, selecione pelo menos uma categoria.')
        else:
            # Filtrar os dados financeiros para exibir apenas as categorias selecionadas
            dados_selecionados = dados_financeiros[['Mês'] + categorias]
            # Exibir opções para seleção do tipo de gráfico para cada categoria
            imagens = []
            for categoria in categorias:
                tipo_grafico = st.sidebar.radio(f'Selecione o Tipo de Gráfico para {categoria}:', ['Gráfico de Barras', 'Gráfico de Linhas', 'Ambos'])

                # Criar o gráfico correspondente ao tipo selecionado
                plt.figure(figsize=(10, 6))

                if tipo_grafico == 'Gráfico de Barras' or tipo_grafico == 'Ambos':
                    plt.bar(dados_financeiros['Mês'], dados_financeiros[categoria], label='Gráfico de Barras')
                if tipo_grafico == 'Gráfico de Linhas' or tipo_grafico == 'Ambos':
                    plt.plot(dados_financeiros['Mês'], dados_financeiros[categoria], label='Gráfico de Linhas')

                plt.title(f'Gastos Mensais - {categoria}')
                plt.xlabel('Mês')
                plt.ylabel('Gastos (R$)')
                plt.xticks(rotation=45)
                plt.legend()
                
                # Salvar o gráfico em um buffer
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                imagens.append(buffer)

            # Botão para gerar relatório
            if st.sidebar.button('Gerar Relatório'):
                gerar_relatorio('Relatório de Análise Financeira', imagens, dados_selecionados)

# Função para criar estilos da tabela
def criar_estilos_tabela():
    styles = getSampleStyleSheet()
    estilo_cabecalho = styles["Normal"]
    estilo_cabecalho.textColor = colors.blue
    estilo_cabecalho.alignment = 1  # Centralizar texto no cabeçalho

    estilo_linha = styles["Normal"]
    estilo_linha.alignment = 1  # Centralizar texto nas linhas normais
    estilo_linha.fontSize = 8

    return estilo_cabecalho, estilo_linha

# Função para criar relatório PDF
def criar_relatorio_pdf(titulo, imagens, dados):
    doc = SimpleDocTemplate(f"{titulo}.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    
    estilo_cabecalho, estilo_linha = criar_estilos_tabela()

    # Adicionar o título ao PDF
    titulo_para = Paragraph(titulo, styles['Title'])
    conteudo = [titulo_para]

    # Adicionar imagens ao PDF
    for imagem in imagens:
        img = Image(imagem, width=400, height=300)
        conteudo.append(img)

    # Adicionar dados (tabela) ao PDF
    dados_list = [dados.columns.values.tolist()] + dados.values.tolist()
    tabela = Table(dados_list)
    tabela.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Cor de fundo para o cabeçalho
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.blue),  # Cor do texto do cabeçalho
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Centralizar texto em toda a tabela
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Adicionar grade à tabela
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),  # Alterar a fonte para negrito
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Tamanho da fonte
    ])
    conteudo.append(tabela)

    # Gerar o PDF
    doc.build(conteudo)
    st.success(f"Relatório '{titulo}.pdf' gerado com sucesso!")

# Botão para gerar relatório em PDF
if uploaded_file is not None and dados_financeiros is not None and categorias:
    if st.sidebar.button('Gerar Relatório em PDF'):
        criar_relatorio_pdf('Relatório de Análise Financeira', imagens, dados_selecionados)
