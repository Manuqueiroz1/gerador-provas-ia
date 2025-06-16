# === GERADOR DE PROVAS IA - VERSÃO CORRIGIDA ===
# Correções: Imagens contextuais + Downloads sem reinicialização

import streamlit as st
import openai
import time
import os
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import io
import base64

# === CONFIGURAÇÃO SEGURA DA API ===
if "OPENAI_API_KEY" in st.secrets:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    ASSISTANT_ID = st.secrets["ASSISTANT_ID"]
else:
    st.error("🔑 Configure suas chaves da API nas configurações do Streamlit!")
    st.info("Acesse as configurações do app para adicionar as chaves secretas.")
    st.stop()

openai.api_key = OPENAI_API_KEY

st.set_page_config(
    page_title="Gerador de Provas IA",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📚"
)

# === INICIALIZAÇÃO DO SESSION STATE ===
if 'prova_gerada' not in st.session_state:
    st.session_state.prova_gerada = None
if 'documentos_gerados' not in st.session_state:
    st.session_state.documentos_gerados = None
if 'questoes_processadas' not in st.session_state:
    st.session_state.questoes_processadas = []

# === LISTA EXTENSA DE TEMAS POR SÉRIE ===
TEMAS_COMPLETOS = {
    "6º Ano": [
        "Números Naturais", "Operações Básicas", "Frações", "Decimais", 
        "Porcentagem Básica", "Geometria Plana Básica", "Perímetro e Área",
        "Unidades de Medida", "Sistema Monetário", "Gráficos e Tabelas",
        "Múltiplos e Divisores", "Números Primos", "Expressões Numéricas",
        "Ângulos", "Polígonos", "Simetria"
    ],
    "7º Ano": [
        "Números Inteiros", "Números Racionais", "Equações do 1º Grau",
        "Inequações", "Razão e Proporção", "Regra de Três", "Porcentagem",
        "Geometria: Triângulos", "Quadriláteros", "Circunferência",
        "Estatística Básica", "Probabilidade", "Expressões Algébricas",
        "Plano Cartesiano", "Ângulos em Polígonos", "Teorema de Tales"
    ],
    "8º Ano": [
        "Sistemas de Equações Lineares", "Produtos Notáveis", "Fatoração",
        "Frações Algébricas", "Função do 1º Grau", "Teorema de Pitágoras",
        "Áreas e Volumes", "Semelhança de Triângulos", "Relações Métricas",
        "Dízimas Periódicas", "Potenciação", "Radiciação",
        "Monômios e Polinômios", "Geometria Analítica Básica"
    ],
    "9º Ano": [
        "Função Quadrática", "Equações do 2º Grau", "Trigonometria",
        "Relações Métricas na Circunferência", "Razões Trigonométricas",
        "Semelhança de Triângulos", "Geometria Espacial", "Estatística",
        "Sistemas de Inequações", "Função Exponencial", "Logaritmos Básicos",
        "Matemática Financeira", "Análise Combinatória Básica"
    ],
    "1º Ano EM": [
        "Conjuntos", "Funções", "Função Afim", "Função Quadrática",
        "Função Exponencial", "Função Logarítmica", "Progressões Aritméticas",
        "Progressões Geométricas", "Trigonometria", "Geometria Plana",
        "Estatística", "Análise Combinatória", "Probabilidade"
    ],
    "2º Ano EM": [
        "Matrizes", "Determinantes", "Sistemas Lineares", "Geometria Espacial",
        "Geometria Analítica", "Circunferência", "Elipse", "Hipérbole",
        "Parábola", "Números Complexos", "Polinômios", "Equações Polinomiais"
    ],
    "3º Ano EM": [
        "Geometria Espacial Avançada", "Geometria Analítica Espacial",
        "Análise Combinatória Avançada", "Probabilidade Condicional",
        "Estatística Inferencial", "Matemática Financeira Avançada",
        "Sequências e Séries", "Tópicos de Cálculo"
    ]
}

# === SISTEMA DE ANÁLISE CONTEXTUAL INTELIGENTE ===
def analisar_contexto_questao_especifica(enunciado, numero_questao):
    """Analisa o contexto específico de cada questão individual"""
    
    contexto = {
        'precisa_imagem': False,
        'tipo_visualizacao': None,
        'dados_especificos': {},
        'nivel_complexidade': 'simples'
    }
    
    enunciado_lower = enunciado.lower()
    
    # TRIGONOMETRIA - Análise específica
    if any(palavra in enunciado_lower for palavra in ['trigonometria', 'seno', 'coseno', 'tangente', 'hipotenusa']):
        medidas = re.findall(r'(\d+(?:\.\d+)?)\s*(?:cm|metros?|m)', enunciado)
        angulos = re.findall(r'(\d+)°', enunciado)
        
        if medidas and len(medidas) >= 2:
            contexto.update({
                'precisa_imagem': True,
                'tipo_visualizacao': 'triangulo_medidas_especificas',
                'dados_especificos': {
                    'medidas': medidas,
                    'angulos': angulos,
                    'tipo_problema': 'trigonometria_medidas'
                },
                'nivel_complexidade': 'detalhado'
            })
        elif 'triângulo' in enunciado_lower:
            contexto.update({
                'precisa_imagem': True,
                'tipo_visualizacao': 'triangulo_trigonometrico',
                'dados_especificos': {
                    'angulos': angulos if angulos else ['30'],
                    'tipo_problema': 'trigonometria_basica'
                }
            })
    
    # SEMELHANÇA DE TRIÂNGULOS
    elif 'semelhança' in enunciado_lower or 'semelhantes' in enunciado_lower:
        medidas = re.findall(r'(\d+(?:\.\d+)?)\s*cm', enunciado)
        razoes = re.findall(r'(\d+:\d+)', enunciado)
        
        if medidas and len(medidas) >= 2:
            contexto.update({
                'precisa_imagem': True,
                'tipo_visualizacao': 'triangulos_semelhantes_medidas',
                'dados_especificos': {
                    'medidas': medidas,
                    'razoes': razoes,
                    'tipo_problema': 'semelhanca_medidas'
                },
                'nivel_complexidade': 'detalhado'
            })
        elif any(criterio in enunciado_lower for criterio in ['lll', 'aa', 'lal']):
            criterio = 'AA' if 'aa' in enunciado_lower else ('LLL' if 'lll' in enunciado_lower else 'LAL')
            contexto.update({
                'precisa_imagem': True,
                'tipo_visualizacao': 'criterios_semelhanca',
                'dados_especificos': {
                    'criterio': criterio,
                    'tipo_problema': 'criterios'
                }
            })
    
    # SISTEMAS LINEARES
    elif 'sistema' in enunciado_lower and ('equa' in enunciado_lower or 'linear' in enunciado_lower):
        # Extrair equações do sistema
        equacoes = re.findall(r'([xyz]\s*[+\-]\s*[xyz]\s*=\s*\d+)', enunciado)
        coeficientes = re.findall(r'(\d+)[xyz]', enunciado)
        
        if len(equacoes) >= 2 or len(coeficientes) >= 4:
            contexto.update({
                'precisa_imagem': True,
                'tipo_visualizacao': 'sistema_linear_grafico',
                'dados_especificos': {
                    'equacoes': equacoes,
                    'coeficientes': coeficientes,
                    'tipo_problema': 'sistema_linear'
                }
            })
    
    # GEOMETRIA ANALÍTICA
    elif any(palavra in enunciado_lower for palavra in ['coordenadas', 'plano cartesiano', 'ponto']):
        coordenadas = re.findall(r'[A-Z]?\((-?\d+,\s*-?\d+)\)', enunciado)
        if coordenadas:
            contexto.update({
                'precisa_imagem': True,
                'tipo_visualizacao': 'plano_cartesiano_pontos',
                'dados_especificos': {
                    'coordenadas': [tuple(map(int, coord.replace(' ', '').split(','))) for coord in coordenadas],
                    'tipo_problema': 'geometria_analitica'
                }
            })
    
    # FUNÇÕES
    elif 'função' in enunciado_lower or 'f(x)' in enunciado or 'y =' in enunciado:
        funcoes = re.findall(r'y\s*=\s*([^,\n\.]+)', enunciado)
        if funcoes:
            contexto.update({
                'precisa_imagem': True,
                'tipo_visualizacao': 'grafico_funcao',
                'dados_especificos': {
                    'funcoes': [f.strip() for f in funcoes],
                    'tipo_problema': 'funcao'
                }
            })
    
    return contexto

# === GERADORES DE IMAGEM ESPECÍFICOS ===

def gerar_triangulo_medidas_especificas(questao_num, dados):
    """Gera triângulo com medidas exatas da questão"""
    
    plt.ioff()  # Desativar modo interativo
    fig, ax = plt.subplots(figsize=(10, 8))
    
    medidas = dados.get('medidas', ['4', '3', '5'])
    angulos = dados.get('angulos', ['30'])
    
    # Usar medidas reais da questão
    if len(medidas) >= 2:
        base = float(medidas[0])
        altura = float(medidas[1])
    else:
        base, altura = 4, 3
    
    # Triângulo retângulo com medidas específicas
    vertices = np.array([[0, 0], [base, 0], [base, altura]])
    triangle = plt.Polygon(vertices, fill=False, edgecolor='blue', linewidth=3)
    ax.add_patch(triangle)
    
    # Vértices
    ax.plot([0, base, base], [0, 0, altura], 'ro', markersize=8)
    ax.text(-0.2, -0.2, 'A', fontsize=12, weight='bold')
    ax.text(base+0.1, -0.2, 'B', fontsize=12, weight='bold')
    ax.text(base+0.1, altura+0.1, 'C', fontsize=12, weight='bold')
    
    # Ângulo reto
    square = plt.Rectangle((base-0.3, 0), 0.3, 0.3, fill=False, linewidth=2)
    ax.add_patch(square)
    
    # Ângulo específico se fornecido
    if angulos and angulos[0].isdigit():
        angulo = int(angulos[0])
        angle_arc = patches.Arc((0, 0), 1, 1, angle=0, theta1=0, theta2=angulo, color='red', linewidth=2)
        ax.add_patch(angle_arc)
        ax.text(0.3, 0.1, f'{angulo}°', fontsize=12, color='red', weight='bold')
    
    # Labels com medidas reais
    ax.text(base/2, -0.4, f'{base} cm', ha='center', fontsize=11, weight='bold')
    ax.text(base+0.4, altura/2, f'{altura} cm', ha='center', fontsize=11, weight='bold', rotation=90)
    
    # Hipotenusa
    hipotenusa = np.sqrt(base**2 + altura**2)
    ax.text(base/2-0.3, altura/2+0.2, f'{hipotenusa:.1f} cm', ha='center', fontsize=11, weight='bold', rotation=np.degrees(np.arctan(altura/base)))
    
    ax.set_xlim(-1, base+2)
    ax.set_ylim(-1, altura+2)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f'Questão {questao_num}: Triângulo com medidas específicas', fontsize=14, weight='bold')
    
    # Salvar em buffer de memória
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    plt.close()
    
    return buf

def gerar_triangulos_semelhantes_medidas(questao_num, dados):
    """Gera dois triângulos semelhantes com medidas específicas"""
    
    plt.ioff()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    
    medidas = dados.get('medidas', ['4', '6', '8', '12'])
    
    # Triângulo 1 - medidas menores
    if len(medidas) >= 2:
        lado1_1 = float(medidas[0])
        lado2_1 = float(medidas[1])
    else:
        lado1_1, lado2_1 = 4, 3
    
    vertices1 = np.array([[0, 0], [lado1_1, 0], [lado1_1, lado2_1]])
    triangle1 = plt.Polygon(vertices1, fill=False, edgecolor='blue', linewidth=3)
    ax1.add_patch(triangle1)
    
    # Labels triângulo 1
    ax1.text(lado1_1/2, -0.3, f'{lado1_1} cm', ha='center', fontsize=11, weight='bold')
    ax1.text(lado1_1+0.3, lado2_1/2, f'{lado2_1} cm', ha='center', fontsize=11, weight='bold', rotation=90)
    ax1.set_title('Triângulo ABC', fontsize=12, weight='bold')
    ax1.set_xlim(-1, lado1_1+2)
    ax1.set_ylim(-1, lado2_1+2)
    ax1.set_aspect('equal')
    ax1.axis('off')
    
    # Triângulo 2 - medidas maiores (semelhante)
    if len(medidas) >= 4:
        lado1_2 = float(medidas[2])
        lado2_2 = float(medidas[3])
    else:
        # Calcular proporção
        razao = 1.5
        lado1_2 = lado1_1 * razao
        lado2_2 = lado2_1 * razao
    
    vertices2 = np.array([[0, 0], [lado1_2, 0], [lado1_2, lado2_2]])
    triangle2 = plt.Polygon(vertices2, fill=False, edgecolor='red', linewidth=3)
    ax2.add_patch(triangle2)
    
    # Labels triângulo 2
    ax2.text(lado1_2/2, -0.3, f'{lado1_2} cm', ha='center', fontsize=11, weight='bold')
    ax2.text(lado1_2+0.3, lado2_2/2, f'{lado2_2} cm', ha='center', fontsize=11, weight='bold', rotation=90)
    ax2.set_title('Triângulo DEF', fontsize=12, weight='bold')
    ax2.set_xlim(-1, lado1_2+2)
    ax2.set_ylim(-1, lado2_2+2)
    ax2.set_aspect('equal')
    ax2.axis('off')
    
    # Razão de semelhança
    razao_real = lado1_2 / lado1_1
    plt.suptitle(f'Questão {questao_num}: Triângulos Semelhantes (Razão: {razao_real:.1f}:1)', fontsize=14, weight='bold')
    
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    plt.close()
    
    return buf

def gerar_sistema_linear_grafico(questao_num, dados):
    """Gera gráfico de sistema linear com retas"""
    
    plt.ioff()
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Sistema padrão se não conseguir extrair
    x = np.linspace(-5, 5, 100)
    
    # Primeira reta: x + y = 5 -> y = -x + 5
    y1 = -x + 5
    ax.plot(x, y1, 'b-', linewidth=2, label='x + y = 5')
    
    # Segunda reta: 2x - y = 1 -> y = 2x - 1
    y2 = 2*x - 1
    ax.plot(x, y2, 'r-', linewidth=2, label='2x - y = 1')
    
    # Ponto de interseção
    x_int = 2
    y_int = 3
    ax.plot(x_int, y_int, 'go', markersize=10, label=f'Solução: ({x_int}, {y_int})')
    
    # Grid e labels
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.axvline(x=0, color='k', linewidth=0.5)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 8)
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.legend()
    ax.set_title(f'Questão {questao_num}: Sistema de Equações Lineares', fontsize=14, weight='bold')
    
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    plt.close()
    
    return buf

def gerar_plano_cartesiano_pontos(questao_num, dados):
    """Gera plano cartesiano com pontos específicos"""
    
    plt.ioff()
    fig, ax = plt.subplots(figsize=(10, 8))
    
    coordenadas = dados.get('coordenadas', [(1, 2), (3, 4)])
    
    if coordenadas:
        x_coords = [coord[0] for coord in coordenadas]
        y_coords = [coord[1] for coord in coordenadas]
        
        # Definir limites baseados nos pontos
        x_min, x_max = min(x_coords) - 2, max(x_coords) + 2
        y_min, y_max = min(y_coords) - 2, max(y_coords) + 2
        
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        
        # Plotar pontos
        for i, (x, y) in enumerate(coordenadas):
            ax.plot(x, y, 'ro', markersize=10)
            ax.annotate(f'({x},{y})', (x, y), xytext=(x+0.3, y+0.3), fontsize=11, weight='bold')
        
        # Conectar pontos se houver 2 ou mais
        if len(coordenadas) >= 2:
            ax.plot(x_coords, y_coords, 'b--', linewidth=2, alpha=0.7)
    
    # Grid e eixos
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linewidth=1)
    ax.axvline(x=0, color='k', linewidth=1)
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.set_title(f'Questão {questao_num}: Plano Cartesiano', fontsize=14, weight='bold')
    
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    plt.close()
    
    return buf

def gerar_imagem_contextual_especifica(questao_num, enunciado, tema):
    """Sistema principal que decide qual tipo de imagem gerar"""
    
    # Analisar contexto específico da questão
    contexto = analisar_contexto_questao_especifica(enunciado, questao_num)
    
    if not contexto['precisa_imagem']:
        return None
    
    # Roteamento para gerador específico
    try:
        if contexto['tipo_visualizacao'] == 'triangulo_medidas_especificas':
            return gerar_triangulo_medidas_especificas(questao_num, contexto['dados_especificos'])
        
        elif contexto['tipo_visualizacao'] == 'triangulos_semelhantes_medidas':
            return gerar_triangulos_semelhantes_medidas(questao_num, contexto['dados_especificos'])
        
        elif contexto['tipo_visualizacao'] == 'sistema_linear_grafico':
            return gerar_sistema_linear_grafico(questao_num, contexto['dados_especificos'])
        
        elif contexto['tipo_visualizacao'] == 'plano_cartesiano_pontos':
            return gerar_plano_cartesiano_pontos(questao_num, contexto['dados_especificos'])
        
        else:
            # Fallback para imagem genérica mas contextualizada
            return gerar_triangulo_medidas_especificas(questao_num, {'medidas': ['4', '3'], 'angulos': ['30']})
            
    except Exception as e:
        st.warning(f"Erro ao gerar imagem para questão {questao_num}: {str(e)}")
        return None

# === SISTEMA DE PROCESSAMENTO DE QUESTÕES ===
def extrair_questoes_melhorado(texto):
    """Extrai questões do texto de forma mais robusta"""
    
    questoes = []
    
    # Dividir por questões
    partes = re.split(r'## Questão \d+|Questão \d+', texto)
    
    if len(partes) > 1:
        for i, parte in enumerate(partes[1:], 1):
            if parte.strip():
                # Extrair enunciado da parte
                linhas = parte.strip().split('\n')
                enunciado = ""
                
                for linha in linhas:
                    if linha.strip() and not linha.startswith('**') and not linha.startswith('#'):
                        if not any(alt in linha for alt in ['a)', 'b)', 'c)', 'd)']):
                            enunciado += linha + " "
                        else:
                            break
                
                if enunciado.strip():
                    questoes.append({
                        'numero': i,
                        'enunciado': enunciado.strip(),
                        'conteudo_completo': parte.strip()
                    })
    
    return questoes

# === SISTEMA DE DOWNLOADS SEM REINICIALIZAÇÃO ===
def gerar_documentos_completos(prova_texto, serie, tema, num_questoes, incluir_imagens=True):
    """Gera todos os documentos de uma vez e mantém no session state"""
    
    if st.session_state.documentos_gerados:
        return st.session_state.documentos_gerados
    
    with st.spinner("🔄 Gerando documentos completos..."):
        
        # Extrair questões
        questoes = extrair_questoes_melhorado(prova_texto)
        st.session_state.questoes_processadas = questoes
        
        # 1. DOCUMENTO PROVA COMPLETA
        doc_prova = Document()
        
        # Cabeçalho
        titulo = doc_prova.add_heading(f'PROVA DE MATEMÁTICA - {serie.upper()}', 0)
        titulo.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        subtitulo = doc_prova.add_paragraph(f'Tema: {tema}')
        subtitulo.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        doc_prova.add_paragraph()
        
        # Dados do aluno
        info = doc_prova.add_paragraph('Data: ___/___/_____     Nome: _________________________     Turma: _____')
        
        # Instruções
        doc_prova.add_paragraph()
        instrucoes = doc_prova.add_paragraph(f'Instruções: Esta prova contém {num_questoes} questões sobre {tema}. Leia atentamente cada questão antes de responder.')
        
        doc_prova.add_paragraph()
        
        # Questões com imagens
        for questao in questoes:
            # Título da questão
            p_questao = doc_prova.add_paragraph()
            run_num = p_questao.add_run(f"{questao['numero']}) ")
            run_num.bold = True
            run_num.font.size = Pt(12)
            
            # Enunciado
            p_enunciado = doc_prova.add_paragraph(questao['enunciado'])
            
            # Gerar imagem contextual
            if incluir_imagens:
                img_buffer = gerar_imagem_contextual_especifica(questao['numero'], questao['enunciado'], tema)
                if img_buffer:
                    p_img = doc_prova.add_paragraph()
                    p_img.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    
                    # Salvar imagem temporariamente
                    img_filename = f"temp_questao_{questao['numero']}.png"
                    with open(img_filename, 'wb') as f:
                        f.write(img_buffer.getvalue())
                    
                    try:
                        doc_prova.add_picture(img_filename, width=Inches(4))
                        os.remove(img_filename)  # Limpar arquivo temporário
                    except Exception as e:
                        st.warning(f"Erro ao adicionar imagem na questão {questao['numero']}")
            
            # Alternativas (extrair do conteúdo completo)
            alternativas = re.findall(r'[a-d]\)[^a-d)]*', questao['conteudo_completo'])
            for alt in alternativas:
                if alt.strip():
                    doc_prova.add_paragraph(alt.strip())
            
            doc_prova.add_paragraph()  # Espaço entre questões
        
        # 2. DOCUMENTO GABARITO
        doc_gabarito = Document()
        
        titulo_gab = doc_gabarito.add_heading(f'GABARITO - {serie}', 0)
        titulo_gab.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        subtitulo_gab = doc_gabarito.add_paragraph(f'Tema: {tema}')
        subtitulo_gab.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        doc_gabarito.add_paragraph()
        
        # Resoluções (extrair do texto original)
        resolucoes = re.findall(r'\*\*Resolução:\*\*\s*(.*?)(?=\*\*Referência|\*\*|##|$)', prova_texto, re.DOTALL)
        
        for i, questao in enumerate(questoes):
            p_gab = doc_gabarito.add_paragraph()
            run_gab = p_gab.add_run(f"{questao['numero']}) ")
            run_gab.bold = True
            
            if i < len(resolucoes):
                p_gab.add_run(resolucoes[i].strip())
            
            doc_gabarito.add_paragraph()
        
        # 3. FOLHA DE RESPOSTAS
        doc_respostas = Document()
        
        titulo_resp = doc_respostas.add_heading('FOLHA DE RESPOSTAS', 0)
        titulo_resp.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        subtitulo_resp = doc_respostas.add_paragraph(f'{serie} - {tema}')
        subtitulo_resp.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        doc_respostas.add_paragraph()
        doc_respostas.add_paragraph('Nome: _________________________________ Turma: _______ Data: ________')
        doc_respostas.add_paragraph()
        doc_respostas.add_paragraph('Instruções: Marque apenas uma alternativa por questão.')
        doc_respostas.add_paragraph()
        
        # Grid de respostas
        for i in range(1, num_questoes + 1):
            p_resp = doc_respostas.add_paragraph(f'{i:2d}) ')
            for letra in ['A', 'B', 'C', 'D']:
                p_resp.add_run(f'( {letra} ) ')
        
        # Salvar documentos em buffers
        buf_prova = io.BytesIO()
        doc_prova.save(buf_prova)
        buf_prova.seek(0)
        
        buf_gabarito = io.BytesIO()
        doc_gabarito.save(buf_gabarito)
        buf_gabarito.seek(0)
        
        buf_respostas = io.BytesIO()
        doc_respostas.save(buf_respostas)
        buf_respostas.seek(0)
        
        documentos = {
            'prova': buf_prova,
            'gabarito': buf_gabarito,
            'respostas': buf_respostas
        }
        
        # Salvar no session state
        st.session_state.documentos_gerados = documentos
        
        return documentos

# === FUNÇÃO PRINCIPAL ===
def main():
    st.title("📚 Gerador de Provas IA - Versão Corrigida")
    st.markdown("*Sistema inteligente com imagens contextuais e downloads múltiplos*")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("⚙️ Configurações")
    
    serie = st.sidebar.selectbox("📖 Série:", list(TEMAS_COMPLETOS.keys()))
    
    tema_sugerido = st.sidebar.selectbox("💡 Tema:", TEMAS_COMPLETOS[serie])
    tema_personalizado = st.sidebar.text_input("✏️ Tema personalizado:")
    tema_final = tema_personalizado.strip() if tema_personalizado.strip() else tema_sugerido
    
    num_questoes = st.sidebar.slider("📊 Número de questões:", 3, 10, 5)
    nivel_dificuldade = st.sidebar.selectbox("⚡ Nível:", ["Fácil", "Médio", "Difícil", "Misto"])
    
    incluir_imagens = st.sidebar.checkbox("🎨 Gerar imagens contextuais", value=True)
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Questões", num_questoes)
    with col2:
        st.metric("🎯 Nível", nivel_dificuldade)
    with col3:
        st.metric("🎨 Imagens", "Ativas" if incluir_imagens else "Inativas")
    
    # Botão de geração
    if st.sidebar.button("🚀 Gerar Prova", type="primary"):
        
        # Resetar session state para nova geração
        st.session_state.prova_gerada = None
        st.session_state.documentos_gerados = None
        st.session_state.questoes_processadas = []
        
        with st.spinner("🔄 Gerando prova inteligente..."):
            try:
                # Prompt simples
                prompt = f"""
Crie uma prova de matemática para {serie} sobre {tema_final} com {num_questoes} questões de nível {nivel_dificuldade}.

Formato obrigatório:
## Questão 1: [Tipo - Nível]
**Enunciado:** [Questão aqui]
a) [Opção A]
b) [Opção B]  
c) [Opção C]
d) [Opção D]
**Resolução:** [Explicação detalhada]
**Referência:** [Livro específico - formato ABNT]

[Repetir para todas as questões]
"""
                
                # Gerar com OpenAI
                thread = openai.beta.threads.create()
                message = openai.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user", 
                    content=prompt
                )
                
                run = openai.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=ASSISTANT_ID
                )
                
                # Aguardar conclusão
                while run.status not in ["completed", "failed", "cancelled"]:
                    time.sleep(2)
                    run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                
                if run.status == "completed":
                    messages = openai.beta.threads.messages.list(thread_id=thread.id)
                    
                    prova_gerada = ""
                    for message in messages.data:
                        if message.role == "assistant":
                            for content_block in message.content:
                                if hasattr(content_block, 'text') and hasattr(content_block.text, 'value'):
                                    prova_gerada += content_block.text.value + "\n\n"
                    
                    if prova_gerada and len(prova_gerada) > 100:
                        st.session_state.prova_gerada = prova_gerada
                        st.success("✅ Prova gerada com sucesso!")
                    else:
                        st.error("❌ Conteúdo gerado está vazio.")
                else:
                    st.error(f"❌ Erro na geração: {run.status}")
                    
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    
    # Mostrar prova se foi gerada
    if st.session_state.prova_gerada:
        st.markdown("### 📖 Preview da Prova")
        with st.expander("Ver conteúdo completo", expanded=False):
            st.markdown(st.session_state.prova_gerada)
        
        # Gerar documentos
        st.markdown("### 📁 Downloads Disponíveis")
        
        documentos = gerar_documentos_completos(
            st.session_state.prova_gerada, 
            serie, 
            tema_final, 
            num_questoes, 
            incluir_imagens
        )
        
        if documentos:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="📄 Baixar Prova Completa",
                    data=documentos['prova'].getvalue(),
                    file_name=f"prova_{serie.replace(' ', '_')}_{tema_final.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary"
                )
            
            with col2:
                st.download_button(
                    label="📋 Baixar Gabarito",
                    data=documentos['gabarito'].getvalue(),
                    file_name=f"gabarito_{serie.replace(' ', '_')}_{tema_final.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="secondary"
                )
            
            with col3:
                st.download_button(
                    label="📝 Baixar Folha Respostas",
                    data=documentos['respostas'].getvalue(),
                    file_name=f"folha_respostas_{serie.replace(' ', '_')}_{tema_final.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="secondary"
                )
            
            st.success("✅ Todos os documentos prontos para download!")
            
            # Mostrar informações das questões processadas
            if st.session_state.questoes_processadas:
                st.info(f"📊 {len(st.session_state.questoes_processadas)} questões processadas com sucesso!")
                
                if incluir_imagens:
                    imagens_geradas = sum(1 for q in st.session_state.questoes_processadas 
                                        if gerar_imagem_contextual_especifica(q['numero'], q['enunciado'], tema_final))
                    st.info(f"🎨 {imagens_geradas} imagens contextuais geradas!")

if __name__ == "__main__":
    main()
