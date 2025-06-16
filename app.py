# === GERADOR DE PROVAS IA - VERSÃO COMPLETA E FUNCIONAL ===
# Mantém todas as funcionalidades importantes com código limpo

import streamlit as st
import openai
import time
import os
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt

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
    page_title="Gerador de Provas IA Completo", 
    layout="wide", 
    initial_sidebar_state="expanded",
    page_icon="📚"
)

# === LISTA EXTENSA DE TEMAS POR SÉRIE ===
TEMAS_COMPLETOS = {
    "6º Ano": [
        "Números Naturais e Sistema Decimal", "Operações com Números Naturais",
        "Múltiplos e Divisores", "Números Primos e Compostos",
        "Frações - Conceitos e Representações", "Operações com Frações",
        "Números Decimais", "Porcentagem Básica",
        "Geometria - Figuras Planas", "Perímetro e Área",
        "Ângulos e Medidas", "Simetria",
        "Unidades de Medida", "Estatística Básica",
        "Gráficos e Tabelas", "Probabilidade Introdutória"
    ],
    
    "7º Ano": [
        "Números Inteiros", "Operações com Números Inteiros",
        "Números Racionais", "Equações do 1º Grau",
        "Inequações do 1º Grau", "Razão e Proporção",
        "Regra de Três Simples", "Porcentagem",
        "Juros Simples", "Geometria - Triângulos",
        "Quadriláteros", "Circunferência e Círculo",
        "Construções Geométricas", "Expressões Algébricas",
        "Monômios e Polinômios", "Estatística Descritiva"
    ],
    
    "8º Ano": [
        "Números Reais", "Radiciação",
        "Potenciação", "Notação Científica",
        "Expressões Algébricas", "Produtos Notáveis",
        "Fatoração", "Frações Algébricas",
        "Equações do 1º Grau com uma Variável", "Sistemas de Equações",
        "Inequações", "Função Afim",
        "Gráficos de Funções", "Geometria - Congruência",
        "Teorema de Pitágoras", "Áreas de Figuras Planas",
        "Volume de Sólidos", "Transformações Geométricas"
    ],
    
    "9º Ano": [
        "Números Reais Completos", "Potências e Raízes",
        "Equações do 2º Grau", "Função Quadrática",
        "Inequações do 2º Grau", "Sistemas de Equações",
        "Semelhança de Triângulos", "Relações Métricas no Triângulo Retângulo",
        "Trigonometria no Triângulo Retângulo", "Circunferência - Ângulos e Arcos",
        "Polígonos Regulares", "Áreas e Volumes",
        "Estatística e Probabilidade", "Progressões Aritméticas",
        "Progressões Geométricas", "Noções de Matemática Financeira"
    ],
    
    "1º Ano EM": [
        "Conjuntos", "Funções - Conceito e Definição",
        "Função Afim", "Função Quadrática",
        "Função Modular", "Função Exponencial",
        "Logaritmos", "Função Logarítmica",
        "Trigonometria - Ciclo Trigonométrico", "Funções Trigonométricas",
        "Equações Trigonométricas", "Progressões Aritméticas",
        "Progressões Geométricas", "Matrizes",
        "Determinantes", "Sistemas Lineares",
        "Análise Combinatória", "Probabilidade"
    ],
    
    "2º Ano EM": [
        "Geometria Analítica - Ponto e Reta", "Distância entre Pontos",
        "Equação da Reta", "Posições entre Retas",
        "Circunferência", "Cônicas - Elipse",
        "Cônicas - Parábola", "Cônicas - Hipérbole",
        "Polinômios", "Equações Polinomiais",
        "Números Complexos", "Estatística Descritiva",
        "Medidas de Tendência Central", "Medidas de Dispersão",
        "Probabilidade Condicional", "Distribuições de Probabilidade"
    ],
    
    "3º Ano EM": [
        "Geometria Espacial - Prismas", "Pirâmides",
        "Cilindros", "Cones",
        "Esferas", "Geometria de Posição",
        "Análise Combinatória Avançada", "Binômio de Newton",
        "Probabilidade e Estatística", "Matemática Financeira",
        "Juros Compostos", "Rendas e Amortizações",
        "Limites", "Noções de Derivadas",
        "Funções Especiais", "Revisão ENEM"
    ]
}

# === SISTEMA DE DETECÇÃO CONTEXTUAL PARA IMAGENS ===
def detectar_necessidade_imagem(enunciado, tema):
    """Detecta automaticamente se a questão precisa de imagem"""
    
    enunciado_lower = enunciado.lower()
    tema_lower = tema.lower()
    
    contexto = {
        'precisa_imagem': False,
        'tipo_imagem': None,
        'elementos': {},
        'prioridade': 'baixa'
    }
    
    # TRIGONOMETRIA
    if any(palavra in tema_lower for palavra in ['trigonometria', 'seno', 'coseno', 'tangente']):
        if any(palavra in enunciado_lower for palavra in ['triângulo', 'ângulo', 'altura', 'cateto', 'hipotenusa']):
            contexto.update({
                'precisa_imagem': True,
                'tipo_imagem': 'triangulo_retangulo',
                'elementos': extrair_elementos_trigonometria(enunciado),
                'prioridade': 'alta'
            })
    
    # GEOMETRIA ANALÍTICA
    elif any(palavra in tema_lower for palavra in ['analítica', 'coordenada', 'plano cartesiano']):
        coordenadas = extrair_coordenadas(enunciado)
        if coordenadas:
            contexto.update({
                'precisa_imagem': True,
                'tipo_imagem': 'plano_cartesiano',
                'elementos': {'pontos': coordenadas},
                'prioridade': 'alta'
            })
    
    # FUNÇÕES
    elif any(palavra in tema_lower for palavra in ['função', 'gráfico']):
        if 'y =' in enunciado or 'f(x)' in enunciado:
            contexto.update({
                'precisa_imagem': True,
                'tipo_imagem': 'grafico_funcao',
                'elementos': extrair_funcoes(enunciado),
                'prioridade': 'alta'
            })
    
    # GEOMETRIA PLANA
    elif any(palavra in enunciado_lower for palavra in ['quadrado', 'retângulo', 'círculo', 'triângulo']):
        contexto.update({
            'precisa_imagem': True,
            'tipo_imagem': 'figura_geometrica',
            'elementos': detectar_figura_geometrica(enunciado),
            'prioridade': 'média'
        })
    
    return contexto

def extrair_elementos_trigonometria(enunciado):
    """Extrai elementos de trigonometria do enunciado"""
    elementos = {}
    
    # Buscar ângulos
    angulos = re.findall(r'(\d+)°', enunciado)
    if angulos:
        elementos['angulos'] = [int(a) for a in angulos]
    
    # Buscar medidas
    medidas = re.findall(r'(\d+(?:\.\d+)?)\s*(?:cm|m|metros?)', enunciado)
    if medidas:
        elementos['medidas'] = [float(m) for m in medidas]
    
    # Detectar tipo de problema
    if any(palavra in enunciado.lower() for palavra in ['árvore', 'sombra', 'prédio']):
        elementos['tipo'] = 'situacao_real'
    else:
        elementos['tipo'] = 'triangulo_generico'
    
    return elementos

def extrair_coordenadas(enunciado):
    """Extrai coordenadas do enunciado"""
    coordenadas = re.findall(r'[A-Z]?\((-?\d+,\s*-?\d+)\)', enunciado)
    pontos = []
    for coord in coordenadas:
        x, y = map(int, coord.replace(' ', '').split(','))
        pontos.append((x, y))
    return pontos

def extrair_funcoes(enunciado):
    """Extrai funções do enunciado"""
    funcoes = re.findall(r'y\s*=\s*([^,\n\.]+)', enunciado)
    return {'funcoes': [f.strip() for f in funcoes]}

def detectar_figura_geometrica(enunciado):
    """Detecta o tipo de figura geométrica"""
    enunciado_lower = enunciado.lower()
    
    if 'quadrado' in enunciado_lower:
        return {'tipo': 'quadrado'}
    elif 'retângulo' in enunciado_lower:
        return {'tipo': 'retangulo'}
    elif 'círculo' in enunciado_lower or 'circunferência' in enunciado_lower:
        return {'tipo': 'circulo'}
    elif 'triângulo' in enunciado_lower:
        return {'tipo': 'triangulo'}
    else:
        return {'tipo': 'generico'}

# === GERADOR DE IMAGENS CONTEXTUAL ===
def gerar_imagem_contextual(questao_num, contexto):
    """Gera imagem baseada no contexto detectado"""
    if not contexto['precisa_imagem']:
        return None
    
    try:
        plt.ioff()  # Desabilitar modo interativo
        
        if contexto['tipo_imagem'] == 'triangulo_retangulo':
            return gerar_triangulo_retangulo(questao_num, contexto['elementos'])
        elif contexto['tipo_imagem'] == 'plano_cartesiano':
            return gerar_plano_cartesiano(questao_num, contexto['elementos'])
        elif contexto['tipo_imagem'] == 'grafico_funcao':
            return gerar_grafico_funcao(questao_num, contexto['elementos'])
        elif contexto['tipo_imagem'] == 'figura_geometrica':
            return gerar_figura_geometrica(questao_num, contexto['elementos'])
        
    except Exception as e:
        st.warning(f"Aviso: Não foi possível gerar imagem para questão {questao_num}: {e}")
        return None

def gerar_triangulo_retangulo(questao_num, elementos):
    """Gera imagem de triângulo retângulo"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Definir vértices do triângulo
    if elementos.get('tipo') == 'situacao_real':
        # Cenário real (árvore, prédio, etc.)
        vertices = np.array([[0, 0], [6, 0], [0, 4]])
        
        # Desenhar árvore/prédio
        ax.plot([0, 0], [0, 4], 'g-', linewidth=6, label='Objeto')
        # Desenhar sombra
        ax.plot([0, 6], [0, 0], 'k-', linewidth=4, label='Sombra')
        # Linha de visão
        ax.plot([0, 6], [4, 0], 'r--', linewidth=2, label='Linha de visão')
    else:
        # Triângulo genérico
        vertices = np.array([[0, 0], [4, 0], [4, 3]])
        triangle = plt.Polygon(vertices, fill=False, edgecolor='blue', linewidth=3)
        ax.add_patch(triangle)
        
        # Marcar ângulo reto
        square = plt.Rectangle((3.7, 0), 0.3, 0.3, fill=False, linewidth=2)
        ax.add_patch(square)
        
        # Labels dos lados
        ax.text(2, -0.3, 'cateto adjacente', ha='center', fontsize=10)
        ax.text(4.3, 1.5, 'cateto oposto', ha='center', fontsize=10, rotation=90)
        ax.text(1.8, 1.8, 'hipotenusa', ha='center', fontsize=10, rotation=37)
    
    # Configurar gráfico
    ax.set_xlim(-1, 8)
    ax.set_ylim(-1, 5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title(f'Questão {questao_num} - Trigonometria', fontsize=14, weight='bold')
    
    # Salvar
    filename = f"questao_{questao_num}_trigonometria.png"
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return filename

def gerar_plano_cartesiano(questao_num, elementos):
    """Gera plano cartesiano com pontos"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    pontos = elementos.get('pontos', [])
    
    if pontos:
        # Definir limites baseados nos pontos
        x_coords = [p[0] for p in pontos]
        y_coords = [p[1] for p in pontos]
        
        x_min, x_max = min(x_coords) - 2, max(x_coords) + 2
        y_min, y_max = min(y_coords) - 2, max(y_coords) + 2
        
        # Plotar pontos
        for i, (x, y) in enumerate(pontos):
            ax.plot(x, y, 'ro', markersize=10)
            ax.annotate(f'({x},{y})', (x, y), xytext=(x+0.3, y+0.3), fontsize=12, weight='bold')
        
        # Se houver 2 pontos, desenhar reta
        if len(pontos) == 2:
            ax.plot([x_coords[0], x_coords[1]], [y_coords[0], y_coords[1]], 'b-', linewidth=2)
    else:
        x_min, x_max, y_min, y_max = -5, 5, -5, 5
    
    # Configurar eixos
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linewidth=1)
    ax.axvline(x=0, color='k', linewidth=1)
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.set_title(f'Questão {questao_num} - Plano Cartesiano', fontsize=14, weight='bold')
    
    # Salvar
    filename = f"questao_{questao_num}_cartesiano.png"
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return filename

def gerar_grafico_funcao(questao_num, elementos):
    """Gera gráfico de função"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    funcoes = elementos.get('funcoes', [])
    x = np.linspace(-10, 10, 400)
    
    for i, funcao in enumerate(funcoes):
        try:
            # Preparar função para avaliação
            funcao_eval = funcao.replace('x', '*x').replace('^', '**').replace('**x', '**2' if 'x2' in funcao else '*x')
            
            # Casos especiais
            if 'x**2' in funcao_eval or 'x²' in funcao:
                y = eval(funcao_eval.replace('x²', 'x**2'), {"x": x, "np": np})
            else:
                y = eval(funcao_eval, {"x": x, "np": np})
            
            ax.plot(x, y, linewidth=2, label=f'y = {funcao}')
        except:
            # Função padrão se não conseguir processar
            y = x
            ax.plot(x, y, linewidth=2, label='y = x')
    
    # Configurar gráfico
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.axvline(x=0, color='k', linewidth=0.5)
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.set_title(f'Questão {questao_num} - Gráfico de Função', fontsize=14, weight='bold')
    ax.legend()
    ax.set_xlim(-5, 5)
    ax.set_ylim(-10, 10)
    
    # Salvar
    filename = f"questao_{questao_num}_funcao.png"
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return filename

def gerar_figura_geometrica(questao_num, elementos):
    """Gera figura geométrica baseada no tipo"""
    fig, ax = plt.subplots(figsize=(6, 6))
    
    tipo = elementos.get('tipo', 'generico')
    
    if tipo == 'quadrado':
        square = plt.Rectangle((1, 1), 3, 3, fill=False, edgecolor='blue', linewidth=3)
        ax.add_patch(square)
        ax.text(2.5, 0.5, 'Quadrado', ha='center', fontsize=12, weight='bold')
    
    elif tipo == 'retangulo':
        rect = plt.Rectangle((0.5, 1.5), 4, 2, fill=False, edgecolor='green', linewidth=3)
        ax.add_patch(rect)
        ax.text(2.5, 1, 'Retângulo', ha='center', fontsize=12, weight='bold')
    
    elif tipo == 'circulo':
        circle = plt.Circle((2.5, 2.5), 1.5, fill=False, edgecolor='red', linewidth=3)
        ax.add_patch(circle)
        ax.text(2.5, 0.5, 'Círculo', ha='center', fontsize=12, weight='bold')
    
    elif tipo == 'triangulo':
        triangle = plt.Polygon([(2.5, 4), (1, 1), (4, 1)], fill=False, edgecolor='purple', linewidth=3)
        ax.add_patch(triangle)
        ax.text(2.5, 0.5, 'Triângulo', ha='center', fontsize=12, weight='bold')
    
    # Configurar gráfico
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title(f'Questão {questao_num} - Geometria', fontsize=14, weight='bold')
    
    # Salvar
    filename = f"questao_{questao_num}_geometria.png"
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return filename

# === SISTEMA DE LIMPEZA DE FORMATAÇÃO MATEMÁTICA ===
def limpar_latex(texto):
    """Remove códigos LaTeX problemáticos"""
    
    # Remover delimitadores LaTeX
    texto = re.sub(r'\\\(([^)]*)\\\)', r'\1', texto)
    texto = re.sub(r'\\\[([^\]]*)\\\]', r'\1', texto)
    
    # Converter frações
    texto = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', texto)
    
    # Converter exponenciais
    texto = re.sub(r'\^2\b', '²', texto)
    texto = re.sub(r'\^3\b', '³', texto)
    texto = re.sub(r'\^{([^}]+)}', r'^(\1)', texto)
    
    # Converter símbolos comuns
    substituicoes = {
        r'\\cdot': '·', r'\\times': '×', r'\\div': '÷',
        r'\\pm': '±', r'\\pi': 'π', r'\\alpha': 'α',
        r'\\beta': 'β', r'\\gamma': 'γ', r'\\theta': 'θ',
        r'\\leq': '≤', r'\\geq': '≥', r'\\neq': '≠',
        r'\\sqrt\{([^}]+)\}': r'√(\1)'
    }
    
    for latex, simbolo in substituicoes.items():
        texto = re.sub(latex, simbolo, texto)
    
    return texto.strip()

# === SISTEMA DE PARSING DE QUESTÕES ===
def extrair_questoes(texto):
    """Extrai questões do texto gerado pela IA"""
    questoes = []
    
    # Dividir por questões
    partes = re.split(r'\n##\s*Questão\s*\d*', texto)
    
    # Primeira parte é introdução
    introducao = partes[0].strip() if partes else ""
    
    # Processar cada questão
    for i, parte in enumerate(partes[1:], 1):
        if parte.strip():
            questao = processar_questao_individual(i, parte)
            if questao:
                questoes.append(questao)
    
    return introducao, questoes

def processar_questao_individual(numero, texto_questao):
    """Processa uma questão individual"""
    questao = {
        'numero': numero,
        'enunciado': '',
        'alternativas': [],
        'resolucao': '',
        'referencia': ''
    }
    
    linhas = texto_questao.split('\n')
    secao_atual = 'enunciado'
    
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
            
        # Detectar seções
        if linha.lower().startswith('**enunciado:**'):
            secao_atual = 'enunciado'
            linha = linha.replace('**Enunciado:**', '').strip()
        elif linha.lower().startswith('**alternativas:**'):
            secao_atual = 'alternativas'
            continue
        elif linha.lower().startswith('**resolução:**') or linha.lower().startswith('**resolucao:**'):
            secao_atual = 'resolucao'
            linha = linha.replace('**Resolução:**', '').replace('**Resolucao:**', '').strip()
        elif linha.lower().startswith('**referência:**') or linha.lower().startswith('**referencia:**'):
            secao_atual = 'referencia'
            linha = linha.replace('**Referência:**', '').replace('**Referencia:**', '').strip()
        
        # Adicionar conteúdo à seção apropriada
        if linha:
            if secao_atual == 'enunciado':
                questao['enunciado'] += linha + ' '
            elif secao_atual == 'alternativas' and re.match(r'^[a-d]\)', linha):
                questao['alternativas'].append(linha)
            elif secao_atual == 'resolucao':
                questao['resolucao'] += linha + ' '
            elif secao_atual == 'referencia':
                questao['referencia'] += linha + ' '
    
    # Limpar espaços extras
    for key in ['enunciado', 'resolucao', 'referencia']:
        questao[key] = questao[key].strip()
    
    return questao if questao['enunciado'] else None

# === CRIAÇÃO DE DOCUMENTOS SEPARADOS ===
def criar_prova_completa(introducao, questoes, serie, tema, incluir_imagens=True):
    """Cria documento com prova completa"""
    doc = Document()
    
    # Cabeçalho
    titulo = doc.add_heading(f'PROVA DE MATEMÁTICA - {serie.upper()}', 0)
    titulo.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    subtitulo = doc.add_paragraph(f'Tema: {tema}')
    subtitulo.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    doc.add_paragraph()
    
    # Dados do aluno
    info = doc.add_paragraph('Data: ___/___/_____     Nome: _________________________________     Turma: _______')
    
    # Instruções
    if introducao:
        instrucoes = extrair_instrucoes(introducao)
        if instrucoes:
            doc.add_paragraph()
            p_inst = doc.add_paragraph(instrucoes)
            p_inst.style = 'Body Text'
    
    doc.add_paragraph()
    
    # Questões
    for questao in questoes:
        # Título da questão
        p_titulo = doc.add_paragraph()
        run_num = p_titulo.add_run(f"{questao['numero']}) ")
        run_num.bold = True
        run_num.font.size = Pt(12)
        
        # Enunciado
        if questao['enunciado']:
            p_enunciado = doc.add_paragraph(questao['enunciado'])
            p_enunciado.style = 'Body Text'
        
        # Gerar imagem se necessário
        if incluir_imagens:
            contexto = detectar_necessidade_imagem(questao['enunciado'], tema)
            if contexto['precisa_imagem']:
                img_file = gerar_imagem_contextual(questao['numero'], contexto)
                if img_file and os.path.exists(img_file):
                    try:
                        doc.add_paragraph()
                        doc.add_picture(img_file, width=Inches(5))
                        doc.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                        os.remove(img_file)  # Limpar arquivo temporário
                    except Exception as e:
                        st.warning(f"Erro ao adicionar imagem: {e}")
        
        # Alternativas
        if questao['alternativas']:
            for alt in questao['alternativas']:
                p_alt = doc.add_paragraph(alt)
                p_alt.paragraph_format.left_indent = Inches(0.5)
        
        doc.add_paragraph()  # Espaço entre questões
    
    return doc

def criar_gabarito_separado(questoes, serie, tema):
    """Cria documento separado com gabarito e resoluções"""
    doc = Document()
    
    # Cabeçalho
    titulo = doc.add_heading(f'GABARITO E RESOLUÇÕES - {serie.upper()}', 0)
    titulo.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    subtitulo = doc.add_paragraph(f'Tema: {tema}')
    subtitulo.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    doc.add_paragraph()
    doc.add_paragraph('Material de apoio para o professor.')
    doc.add_paragraph()
    
    # Resoluções
    for questao in questoes:
        # Questão
        p_questao = doc.add_paragraph()
        run_num = p_questao.add_run(f"Questão {questao['numero']}: ")
        run_num.bold = True
        run_num.font.size = Pt(12)
        
        # Resolução
        if questao['resolucao']:
            doc.add_paragraph(questao['resolucao'])
        
        # Referência
        if questao['referencia']:
            p_ref = doc.add_paragraph()
            run_ref = p_ref.add_run('Referência: ')
            run_ref.bold = True
            p_ref.add_run(questao['referencia'])
        
        doc.add_paragraph()
    
    return doc

def criar_folha_respostas(num_questoes, serie, tema):
    """Cria folha de respostas separada"""
    doc = Document()
    
    # Cabeçalho
    titulo = doc.add_heading('FOLHA DE RESPOSTAS', 0)
    titulo.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    subtitulo = doc.add_paragraph(f'{serie} - {tema}')
    subtitulo.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    doc.add_paragraph()
    
    # Dados do aluno
    doc.add_paragraph('Nome: _____________________________________________ Turma: _______ Data: ________')
    doc.add_paragraph()
    doc.add_paragraph('Instruções: Marque apenas uma alternativa por questão.')
    doc.add_paragraph()
    
    # Grid de respostas
    for i in range(1, num_questoes + 1):
        p = doc.add_paragraph(f'{i:2d}) ')
        for letra in ['A', 'B', 'C', 'D']:
            p.add_run(f'( {letra} ) ')
        
        # Quebra de linha a cada 10 questões
        if i % 10 == 0:
            doc.add_paragraph()
    
    return doc

def extrair_instrucoes(introducao):
    """Extrai instruções da introdução"""
    linhas = introducao.split('\n')
    instrucoes = []
    
    for linha in linhas:
        linha = linha.strip()
        if ('instruções' in linha.lower() or 
            'tempo' in linha.lower() or
            'questões' in linha.lower()):
            instrucoes.append(linha)
    
    return ' '.join(instrucoes)

# === PROMPT OTIMIZADO ===
def criar_prompt_otimizado(serie, tema, num_questoes, nivel_dificuldade):
    """Cria prompt otimizado para geração de provas"""
    
    distribuicao = calcular_distribuicao_dificuldade(num_questoes, nivel_dificuldade)
    tempo_estimado = num_questoes * 6  # 6 min por questão
    
    return f"""
Crie uma prova de matemática completa para {serie} sobre o tema "{tema}" com {num_questoes} questões.

⚠️ FORMATAÇÃO MATEMÁTICA OBRIGATÓRIA:
- NÃO use códigos LaTeX como \\( \\) ou \\[ \\]
- Use símbolos Unicode diretos: ², ³, √, ÷, ×, ±, π, α, β
- Para frações use: (a)/(b) em vez de \\frac{{a}}{{b}}
- Para exponenciais use: x² ou x^2 (sem barras invertidas)
- Para coordenadas use: A(1, 3) sem delimitadores LaTeX

⚠️ REFERÊNCIAS OBRIGATÓRIAS:
- Cada questão DEVE ter uma referência bibliográfica específica
- Use livros de matemática conhecidos
- Formate as referências em padrão ABNT

DISTRIBUIÇÃO DE DIFICULDADE:
- Questões fáceis: {distribuicao['fácil']}
- Questões médias: {distribuicao['médio']}  
- Questões difíceis: {distribuicao['difícil']}

FORMATO OBRIGATÓRIO:

# Prova de Matemática - {serie}: {tema}

**Instruções:** Esta prova contém {num_questoes} questões sobre {tema}. Leia atentamente cada questão antes de responder. Marque apenas uma alternativa por questão.

**Tempo estimado:** {tempo_estimado} minutos

## Questão 1: [Tipo - Nível]
**Enunciado:** [Questão aqui - SEM códigos LaTeX]
**Alternativas:**
a) [Opção A - formatação limpa]
b) [Opção B - formatação limpa] 
c) [Opção C - formatação limpa]
d) [Opção D - formatação limpa]
**Resolução:** [Explicação detalhada com cálculos limpos]
**Referência:** [Cite livro específico - formato ABNT completo]

[Repetir para todas as {num_questoes} questões]

## REFERÊNCIAS BIBLIOGRÁFICAS
[Liste todas as referências citadas, formatadas em ABNT]

CRITÉRIOS OBRIGATÓRIOS:
- Cada questão DEVE ter uma referência específica
- Formatação matemática LIMPA (sem LaTeX)
- Varie as referências entre questões
- Use apenas símbolos Unicode ou texto simples
"""

def calcular_distribuicao_dificuldade(num_questoes, nivel_dificuldade):
    """Calcula distribuição de questões por dificuldade"""
    if nivel_dificuldade == "Fácil":
        return {"fácil": num_questoes, "médio": 0, "difícil": 0}
    elif nivel_dificuldade == "Médio":
        return {"fácil": 0, "médio": num_questoes, "difícil": 0}
    elif nivel_dificuldade == "Difícil":
        return {"fácil": 0, "médio": 0, "difícil": num_questoes}
    else:  # Misto
        facil = max(1, num_questoes // 3)
        dificil = max(1, num_questoes // 3)
        medio = num_questoes - facil - dificil
        return {"fácil": facil, "médio": medio, "difícil": dificil}

# === COMUNICAÇÃO COM OPENAI ===
def obter_resposta_openai(thread):
    """Obtém resposta completa do OpenAI"""
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    conteudo_completo = ""
    
    for message in messages.data:
        if message.role == "assistant":
            for content_block in message.content:
                if hasattr(content_block, 'text') and hasattr(content_block.text, 'value'):
                    conteudo_completo += content_block.text.value + "\n\n"
    
    return conteudo_completo.strip()

# === INTERFACE PRINCIPAL ===
def main():
    st.title("📚 Gerador de Provas IA - Versão Completa")
    st.markdown("*Sistema inteligente com gerador de imagens contextual e downloads separados*")
    st.markdown("---")
    
    # Validação de configuração
    if OPENAI_API_KEY == "sua_chave_openai_aqui":
        st.error("❌ Configure sua chave da API OpenAI na variável OPENAI_API_KEY!")
        st.info("💡 Edite o código e substitua 'sua_chave_openai_aqui' pela sua chave real.")
        st.stop()
    
    # Sidebar - Configurações
    st.sidebar.header("⚙️ Configurações da Prova")
    
    # Série
    serie = st.sidebar.selectbox(
        "📖 Série:",
        ["6º Ano", "7º Ano", "8º Ano", "9º Ano", "1º Ano EM", "2º Ano EM", "3º Ano EM"]
    )
    
    # Tema
    temas_disponiveis = TEMAS_COMPLETOS.get(serie, [])
    tema_selecionado = st.sidebar.selectbox("💡 Tema:", temas_disponiveis)
    
    # Tema personalizado
    tema_personalizado = st.sidebar.text_input("✏️ Tema personalizado (opcional):")
    tema_final = tema_personalizado.strip() if tema_personalizado.strip() else tema_selecionado
    
    # Configurações da prova
    st.sidebar.markdown("### 🎯 Configurações")
    num_questoes = st.sidebar.slider("📊 Número de questões:", 3, 15, 5)
    nivel_dificuldade = st.sidebar.selectbox(
        "⚡ Nível de Dificuldade:",
        ["Fácil", "Médio", "Difícil", "Misto"]
    )
    
    # Opções avançadas
    st.sidebar.markdown("### 🎨 Recursos Avançados")
    incluir_imagens = st.sidebar.checkbox("🖼️ Gerar imagens contextuais", value=True)
    limpar_formatacao = st.sidebar.checkbox("🧹 Limpar códigos LaTeX", value=True)
    
    # Downloads separados
    st.sidebar.markdown("### 📁 Downloads Separados")
    gerar_gabarito_separado = st.sidebar.checkbox("📋 Gabarito e resoluções separados", value=True)
    gerar_folha_separada = st.sidebar.checkbox("📝 Folha de respostas separada", value=True)
    
    # Informações da prova
    tempo_estimado = num_questoes * 6
    st.sidebar.markdown("---")
    st.sidebar.info(f"**📊 Resumo:**\n"
                   f"• Série: {serie}\n"
                   f"• Tema: {tema_final}\n"
                   f"• Questões: {num_questoes}\n"
                   f"• Nível: {nivel_dificuldade}\n"
                   f"• Tempo: {tempo_estimado} min\n"
                   f"• Imagens: {'✅' if incluir_imagens else '❌'}")
    
    # Área principal
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Questões", num_questoes)
    with col2:
        st.metric("⏱️ Tempo", f"{tempo_estimado} min")
    with col3:
        st.metric("🎯 Nível", nivel_dificuldade)
    with col4:
        st.metric("🎨 Recursos", "Ativados" if incluir_imagens else "Básicos")
    
    # Botão de geração
    if st.button("🚀 Gerar Prova Completa", type="primary"):
        
        with st.spinner("🔄 Gerando prova inteligente..."):
            try:
                # Criar prompt
                prompt = criar_prompt_otimizado(serie, tema_final, num_questoes, nivel_dificuldade)
                
                # Comunicar com OpenAI
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
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                step = 0
                while run.status not in ["completed", "failed", "cancelled"]:
                    time.sleep(2)
                    run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                    step += 1
                    progress = min(step * 10, 95)
                    progress_bar.progress(progress)
                    progress_text.text(f"⏳ Processando... {progress}%")
                
                progress_bar.progress(100)
                progress_text.text("✅ Prova gerada!")
                
                if run.status == "completed":
                    # Obter resposta
                    texto_prova = obter_resposta_openai(thread)
                    
                    if texto_prova and len(texto_prova) > 100:
                        st.success("✅ Prova gerada com sucesso!")
                        
                        # Limpar formatação se solicitado
                        if limpar_formatacao:
                            texto_prova = limpar_latex(texto_prova)
                            st.info("🧹 Formatação matemática limpa aplicada")
                        
                        # Processar questões
                        introducao, questoes = extrair_questoes(texto_prova)
                        
                        if questoes:
                            st.success(f"✅ {len(questoes)} questões processadas com sucesso!")
                            
                            # Preview
                            st.markdown("### 📖 Preview da Prova")
                            with st.expander("Ver conteúdo completo"):
                                st.markdown(texto_prova)
                            
                            # Gerar documentos
                            st.markdown("### 🔧 Gerando Documentos")
                            
                            # Prova completa
                            doc_prova = criar_prova_completa(introducao, questoes, serie, tema_final, incluir_imagens)
                            timestamp = time.strftime("%Y%m%d_%H%M%S")
                            nome_prova = f"prova_{serie.replace(' ', '_').lower()}_{tema_final.replace(' ', '_').lower()}_{timestamp}.docx"
                            doc_prova.save(nome_prova)
                            
                            documentos_gerados = []
                            documentos_gerados.append(("📄 Prova Completa", nome_prova))
                            
                            # Gabarito separado
                            if gerar_gabarito_separado:
                                doc_gabarito = criar_gabarito_separado(questoes, serie, tema_final)
                                nome_gabarito = f"gabarito_{serie.replace(' ', '_').lower()}_{tema_final.replace(' ', '_').lower()}_{timestamp}.docx"
                                doc_gabarito.save(nome_gabarito)
                                documentos_gerados.append(("📋 Gabarito e Resoluções", nome_gabarito))
                            
                            # Folha de respostas
                            if gerar_folha_separada:
                                doc_folha = criar_folha_respostas(num_questoes, serie, tema_final)
                                nome_folha = f"folha_respostas_{serie.replace(' ', '_').lower()}_{tema_final.replace(' ', '_').lower()}_{timestamp}.docx"
                                doc_folha.save(nome_folha)
                                documentos_gerados.append(("📝 Folha de Respostas", nome_folha))
                            
                            # Downloads
                            st.markdown("### 📁 Downloads Disponíveis")
                            
                            cols = st.columns(len(documentos_gerados))
                            for i, (titulo, arquivo) in enumerate(documentos_gerados):
                                with cols[i]:
                                    if os.path.exists(arquivo):
                                        with open(arquivo, "rb") as file_obj:
                                            st.download_button(
                                                label=f"⬇️ {titulo}",
                                                data=file_obj.read(),
                                                file_name=arquivo,
                                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                                type="primary" if i == 0 else "secondary"
                                            )
                            
                            # Informações finais
                            st.markdown("---")
                            st.info(f"📋 **Resumo dos arquivos gerados:**\n"
                                   f"• {len(questoes)} questões de nível {nivel_dificuldade.lower()}\n"
                                   f"• Tempo estimado: {tempo_estimado} minutos\n"
                                   f"• {'Imagens contextuais incluídas' if incluir_imagens else 'Apenas texto'}\n"
                                   f"• {len(documentos_gerados)} documentos gerados")
                            
                        else:
                            st.error("❌ Nenhuma questão foi encontrada no texto gerado")
                            st.text_area("Conteúdo recebido:", texto_prova, height=200)
                    else:
                        st.error("❌ Conteúdo gerado está vazio ou muito curto")
                else:
                    st.error(f"❌ Erro na geração: {run.status}")
                    
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
                st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    

        🤖 Gerador de Provas IA - Versão Completa

        ✨ Gerador de imagens contextual • 📚 Lista extensa de temas • 🔧 Downloads separados
    

    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
