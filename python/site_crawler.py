import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import time
import re # Biblioteca para expressões regulares, útil para buscas flexíveis
import glob
from datetime import datetime
import urllib.parse
from datetime import datetime, timedelta
import warnings
import urllib3

# Desabilita avisos de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

def normalizar_data(data_str):
    """
    Converte uma string de data em diferentes formatos para dd/mm/yyyy
    """
    meses = {
        'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
        'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
        'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12',
        'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'mai': '05',
        'jun': '06', 'jul': '07', 'ago': '08', 'set': '09', 'out': '10',
        'nov': '11', 'dez': '12'
    }
    
    try:
        # Remove dia da semana se presente
        dias_semana = r'(?:segunda|terça|quarta|quinta|sexta|sábado|domingo),?\s*'
        data_str = re.sub(dias_semana, '', data_str, flags=re.IGNORECASE)
        
        # Formato: dd/mm/yyyy ou dd/mm/yy
        if re.match(r'\d{2}/\d{2}/\d{2,4}', data_str):
            dia, mes, ano = data_str.split('/')
            if len(ano) == 2:
                ano = '20' + ano
            return f"{dia.zfill(2)}/{mes.zfill(2)}/{ano}"
            
        # Formato: dd.mm.yyyy ou dd-mm-yyyy
        elif re.match(r'\d{2}[.-]\d{2}[.-]\d{2,4}', data_str):
            dia, mes, ano = re.split(r'[.-]', data_str)
            if len(ano) == 2:
                ano = '20' + ano
            return f"{dia.zfill(2)}/{mes.zfill(2)}/{ano}"
            
        # Formato: dd de mês de yyyy
        elif re.search(r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}', data_str, re.IGNORECASE):
            partes = re.search(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})', data_str, re.IGNORECASE)
            dia = partes.group(1)
            mes = meses[partes.group(2).lower()]
            ano = partes.group(3)
            return f"{dia.zfill(2)}/{mes}/{ano}"
            
        # Formato: mês de yyyy
        elif re.search(r'(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+\d{4}', data_str, re.IGNORECASE):
            partes = re.search(r'(\w+)\s+de\s+(\d{4})', data_str, re.IGNORECASE)
            mes = meses[partes.group(1).lower()]
            ano = partes.group(2)
            return f"01/{mes}/{ano}"
            
        # Formato: dd/mmm/yyyy
        elif re.match(r'\d{1,2}/(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)/\d{2,4}', data_str, re.IGNORECASE):
            dia, mes, ano = data_str.split('/')
            if len(ano) == 2:
                ano = '20' + ano
            return f"{dia.zfill(2)}/{meses[mes.lower()]}/{ano}"
            
        return data_str
    except:
        return data_str

# Padrões de elementos HTML que podem conter datas
ELEMENTOS_DATA = {
    'tabela': [
        'cronograma', 'datas', 'calendario', 'prazos', 'schedule', 'timeline',
        'períodos', 'etapas', 'fases', 'dates', 'deadlines', 'horários',
        'programação', 'agenda', 'período', 'informações', 'inscrição', 'evento'
    ],
    'titulo': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b', 'em'],
    'lista': ['ul', 'ol', 'dl'],
    'div': [
        'calendar', 'schedule', 'cronograma', 'datas', 'prazos', 'período',
        'timeline', 'dates', 'info', 'content', 'main', 'article', 'section',
        'inscricao', 'evento', 'feira', 'olimpiada', 'mostra'
    ],
    'link': [
        'edital', 'regulamento', 'inscricao', 'registro', 'calendario',
        'cronograma', 'datas', 'informacoes', 'participe', 'participate'
    ],
    'especifico': [
        'datetime', 'date', 'time', 'schedule-date', 'event-date',
        'registration-date', 'deadline-date', 'post-date'
    ]
}

# Padrões de textos que indicam datas
PADROES_CONTEXTO = {
    'inscricao_inicio': [
        # Padrões diretos de início
        r'in[ií]cio\s+das?\s+inscri[çc][oõ]e?s',
        r'abertura\s+das?\s+inscri[çc][oõ]e?s',
        r'per[ií]odo\s+de\s+inscri[çc][oõ]e?s.{0,20}(?:come[çc]a|inicia)',
        r'inscri[çc][oõ]e?s\s+(?:a partir de|começam em)',
        r'data\s+de\s+in[ií]cio\s+das?\s+inscri[çc][oõ]e?s',
        r'primeira\s+data\s+para\s+inscri[çc][oõ]e?s',
        
        # Padrões de início de etapas
        r'in[ií]cio\s+das?\s+submiss[oõ]e?s',
        r'abertura\s+das?\s+submiss[oõ]e?s',
        r'in[ií]cio\s+do\s+cadastro',
        r'abertura\s+do\s+sistema',
        
        # Padrões contextuais
        r'(?:sistema|plataforma|portal)\s+(?:abre|disponível)\s+(?:para|em)',
        r'primeira\s+fase\s+de\s+inscri[çc][oõ]e?s',
        r'come[çc]am\s+as\s+inscri[çc][oõ]e?s',
        r'inscri[çc][oõ]e?s\s+(?:liberadas|disponíveis)',
    ],
    'inscricao_fim': [
        # Padrões diretos de término
        r'(?:fim|t[ée]rmino|encerramento)\s+das?\s+inscri[çc][oõ]e?s',
        r'inscri[çc][oõ]e?s\s+at[ée]',
        r'prazo\s+(?:final|limite)\s+(?:para|das)\s+inscri[çc][oõ]e?s',
        r'[úu]ltimo\s+dia\s+(?:para|das)\s+inscri[çc][oõ]e?s',
        r'data\s+limite\s+(?:para|das)\s+inscri[çc][oõ]e?s',
        r'encerram(?:-se)?\s+as\s+inscri[çc][oõ]e?s',
        
        # Padrões de término de etapas
        r'(?:fim|término|encerramento)\s+das?\s+submiss[oõ]e?s',
        r'(?:fim|término|encerramento)\s+do\s+cadastro',
        r'fechamento\s+do\s+sistema',
        
        # Padrões contextuais
        r'data\s+m[áa]xima\s+para\s+(?:envio|submiss[ãa]o)',
        r'[úu]ltima\s+data\s+(?:para|das)\s+inscri[çc][oõ]e?s',
        r'prazo\s+encerra(?:-se)?',
        r'(?:sistema|plataforma|portal)\s+fecha(?:\s+para\s+inscri[çc][oõ]e?s)?',
    ],
    'evento_inicio': [
        # Padrões diretos de início do evento
        r'in[ií]cio\s+d[ao]\s+(?:feira|evento|mostra|apresenta[çc][aã]o|olimp[ií]ada)',
        r'abertura\s+d[ao]\s+(?:feira|evento|mostra|olimp[ií]ada)',
        r'(?:feira|evento|mostra|olimp[ií]ada)\s+come[çc]a',
        r'cerim[ôo]nia\s+de\s+abertura',
        r'data\s+de\s+in[ií]cio\s+do\s+evento',
        
        # Padrões de início de atividades
        r'in[ií]cio\s+das?\s+apresenta[çc][oõ]e?s',
        r'primeiro\s+dia\s+d[ao]\s+(?:feira|evento|mostra)',
        r'abertura\s+oficial',
        
        # Padrões contextuais
        r'realiza[çc][ãa]o\s+d[ao]\s+(?:feira|evento|mostra)\s+em',
        r'data\s+d[ao]\s+(?:feira|evento|mostra)',
        r'acontecer[áa]\s+(?:em|no\s+dia)',
        r'(?:feira|evento|mostra)\s+ser[áa]\s+realizada?',
    ],
    'evento_fim': [
        # Padrões diretos de término
        r'(?:fim|t[ée]rmino|encerramento)\s+d[ao]\s+(?:feira|evento|mostra|olimp[ií]ada)',
        r'(?:feira|evento|mostra|olimp[ií]ada)\s+termina',
        r'cerim[ôo]nia\s+de\s+encerramento',
        r'[úu]ltimo\s+dia\s+d[ao]\s+(?:feira|evento|mostra)',
        r'data\s+de\s+(?:encerramento|t[ée]rmino)\s+do\s+evento',
        
        # Padrões de término de atividades
        r'encerramento\s+das?\s+apresenta[çc][oõ]e?s',
        r'[úu]ltimo\s+dia\s+de\s+atividades',
        r'encerramento\s+oficial',
        
        # Padrões contextuais
        r'(?:feira|evento|mostra)\s+vai\s+at[ée]',
        r'final\s+d[ao]\s+(?:feira|evento|mostra)',
        r'at[ée]\s+o\s+dia',
        r'(?:feira|evento|mostra)\s+se\s+encerra',
    ]
}

# Padrões de datas em diferentes formatos
PADROES_DATA = [
    # Formatos básicos
    r'\d{2}/\d{2}/\d{2,4}',  # dd/mm/yyyy ou dd/mm/yy
    r'\d{2}\.\d{2}\.\d{2,4}',  # dd.mm.yyyy ou dd.mm.yy
    r'\d{2}-\d{2}-\d{2,4}',  # dd-mm-yyyy ou dd-mm-yy
    r'\d{4}/\d{2}/\d{2}',  # yyyy/mm/dd
    r'\d{4}-\d{2}-\d{2}',  # yyyy-mm-dd
    
    # Formatos com mês por extenso
    r'\d{1,2}\s+de\s+(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+\d{4}',  # dd de mês de yyyy
    r'(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+\d{4}',  # mês de yyyy
    r'\d{1,2}/(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)/\d{2,4}',  # dd/mmm/yyyy
    
    # Formatos com dia da semana
    r'(?:segunda|terça|quarta|quinta|sexta|sábado|domingo)(?:-feira)?,?\s+\d{1,2}\s+de\s+(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+\d{4}',  # dia da semana, dd de mês de yyyy
    r'(?:seg|ter|qua|qui|sex|sáb|dom)\.,?\s+\d{1,2}/\d{2}/\d{4}',  # dia abreviado, dd/mm/yyyy
    
    # Formatos com contexto de prazo
    r'(?:até|deadline|prazo|limite).*?(\d{2}/\d{2}/\d{2,4})',  # Prazo até dd/mm/yyyy
    r'(?:até|deadline|prazo|limite).*?(\d{1,2}\s+de\s+(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+\d{4})',  # Prazo até dd de mês de yyyy
    
    # Formatos de período
    r'(?:de|entre|a partir de|começa|inicia)(?:\s+em)?\s+(\d{2}/\d{2}/\d{2,4})\s+(?:até|a|e|ao?)\s+(\d{2}/\d{2}/\d{2,4})',  # Período de dd/mm/yyyy até dd/mm/yyyy
    r'(?:de|entre|a partir de|começa|inicia)(?:\s+em)?\s+(\d{1,2}\s+de\s+(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+\d{4})\s+(?:até|a|e|ao?)\s+(\d{1,2}\s+de\s+(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+\d{4})',  # Período de dd de mês de yyyy até dd de mês de yyyy
    
    # Formatos com hora (ignorando a parte da hora)
    r'\d{2}/\d{2}/\d{4}\s+(?:\d{2}:\d{2}(?::\d{2})?)?',  # dd/mm/yyyy hh:mm(:ss)
    r'\d{1,2}\s+de\s+(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+\d{4}\s+(?:às|as|-)?\s+\d{2}:\d{2}(?::\d{2})?',  # dd de mês de yyyy às hh:mm(:ss)
    
    # Formatos especiais
    r'(?:início|começo|abertura|encerramento|fim|término):\s*\d{2}/\d{2}/\d{4}',  # Palavras-chave: dd/mm/yyyy
    r'data\s*(?:inicial|final|limite):\s*\d{2}/\d{2}/\d{4}',  # Data inicial/final/limite: dd/mm/yyyy
]

def extrair_datas_elemento(elemento, contexto=''):
    """
    Extrai datas de um elemento HTML específico com seu contexto,
    considerando elementos vizinhos e estrutura do documento
    """
    datas = []
    texto_principal = elemento.get_text(separator=' ', strip=True)
    
    # Coleta elementos de contexto
    elementos_contexto = {
        'anterior': None,
        'proximo': None,
        'pai': None,
        'filhos': [],
        'irmaos': []
    }
    
    # Encontra elementos vizinhos
    elementos_contexto['anterior'] = elemento.find_previous_sibling()
    elementos_contexto['proximo'] = elemento.find_next_sibling()
    elementos_contexto['pai'] = elemento.parent
    
    # Encontra elementos irmãos com conteúdo relevante
    if elementos_contexto['pai']:
        for irmao in elementos_contexto['pai'].children:
            if hasattr(irmao, 'name') and irmao != elemento:
                # Verifica se o elemento irmão tem texto relevante
                texto_irmao = irmao.get_text(strip=True)
                if texto_irmao and any(termo in texto_irmao.lower() for termo_lista in ELEMENTOS_DATA.values() for termo in termo_lista):
                    elementos_contexto['irmaos'].append(irmao)
    
    # Encontra elementos filhos com conteúdo relevante
    for filho in elemento.children:
        if hasattr(filho, 'name'):
            texto_filho = filho.get_text(strip=True)
            if texto_filho and any(termo in texto_filho.lower() for termo_lista in ELEMENTOS_DATA.values() for termo in termo_lista):
                elementos_contexto['filhos'].append(filho)
    
    # Processa cada padrão de data
    for padrao in PADROES_DATA:
        datas_encontradas = re.finditer(padrao, texto_principal, re.IGNORECASE)
        for match in datas_encontradas:
            data = match.group()
            
            # Coleta contexto ao redor da data
            pre_contexto = texto_principal[max(0, match.start() - 100):match.start()].lower()
            pos_contexto = texto_principal[match.end():min(len(texto_principal), match.end() + 100)].lower()
            
            # Adiciona contexto dos elementos vizinhos
            contextos_adicionais = []
            
            # Adiciona texto de elementos relevantes
            for tipo, elem in elementos_contexto.items():
                if tipo == 'anterior' and elem:
                    contextos_adicionais.append(elem.get_text(strip=True))
                elif tipo == 'proximo' and elem:
                    contextos_adicionais.append(elem.get_text(strip=True))
                elif tipo == 'pai' and elem:
                    # Verifica se o pai tem algum atributo relevante
                    for attr in ['title', 'aria-label', 'data-description']:
                        if elem.has_attr(attr):
                            contextos_adicionais.append(elem[attr])
                elif tipo in ['filhos', 'irmaos']:
                    for e in elem:
                        contextos_adicionais.append(e.get_text(strip=True))
            
            # Combina todos os contextos
            contexto_total = ' '.join([pre_contexto, pos_contexto] + contextos_adicionais)
            
            # Limpa e normaliza o contexto
            contexto_total = ' '.join(contexto_total.lower().split())
            
            # Normaliza a data encontrada
            data_norm = normalizar_data(data)
            
            # Verifica se a data já foi encontrada para evitar duplicatas
            data_info = {
                'data': data_norm,
                'contexto': contexto_total,
                'elemento_tipo': elemento.name,
                'classe': elemento.get('class', ''),
                'id': elemento.get('id', '')
            }
            
            # Só adiciona se a data ainda não foi encontrada neste elemento
            if not any(d['data'] == data_norm and d['contexto'] == contexto_total for d in datas):
                datas.append(data_info)
    
    return datas

# Lista de URLs das olimpíadas que você quer analisar.
# Este é o seu "parâmetro" principal. Você pode adicionar quantos links quiser.
URLS_OLIMPIADAS = [
    'https://www.oba.org.br/site/',    # Exemplo: Olimpíada Brasileira de Astronomia
    'https://www.obm.org.br/',         # Exemplo: Olimpíada Brasileira de Matemática
    'https://www.obr.org.br/',         # Exemplo: Olimpíada Brasileira de Robótica
    # Adicione outros links aqui
]

# Cabeçalho da requisição para simular um navegador e evitar ser bloqueado.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Função para classificar datas baseado no contexto
def classificar_data(data_str, texto_contexto, posicao_na_sequencia=None, info_elemento=None):
    """
    Classifica uma data com base no texto ao seu redor, estrutura HTML e posição na sequência
    """
    texto_contexto = texto_contexto.lower()
    pontuacao = {
        'inscricao_inicio': 0,
        'inscricao_fim': 0,
        'evento_inicio': 0,
        'evento_fim': 0
    }
    
    # 1. Classificação por padrões de contexto explícitos
    for tipo_data, padroes in PADROES_CONTEXTO.items():
        for padrao in padroes:
            matches = re.finditer(padrao, texto_contexto, re.IGNORECASE)
            for match in matches:
                # Quanto mais próximo o padrão estiver da data, maior a pontuação
                distancia = min(abs(match.start()), abs(match.end()))
                pontuacao[tipo_data] += max(0, (1000 - distancia) / 1000)
    
    # 2. Análise estrutural do HTML
    if info_elemento:
        elemento_tipo = info_elemento.get('elemento_tipo', '')
        elemento_classe = ' '.join(info_elemento.get('classe', [])) if isinstance(info_elemento.get('classe'), list) else str(info_elemento.get('classe', ''))
        elemento_id = info_elemento.get('id', '')
        
        # Elementos que sugerem início
        inicio_patterns = ['start', 'begin', 'first', 'opening', 'inicio', 'começo', 'abertura']
        # Elementos que sugerem fim
        fim_patterns = ['end', 'finish', 'last', 'closing', 'fim', 'termino', 'encerramento']
        # Elementos que sugerem inscrição
        inscricao_patterns = ['registration', 'subscribe', 'inscricao', 'cadastro']
        # Elementos que sugerem evento
        evento_patterns = ['event', 'fair', 'show', 'evento', 'feira', 'mostra']
        
        for pattern in inicio_patterns:
            if pattern in elemento_classe.lower() or pattern in elemento_id.lower():
                pontuacao['inscricao_inicio'] += 0.5
                pontuacao['evento_inicio'] += 0.5
                
        for pattern in fim_patterns:
            if pattern in elemento_classe.lower() or pattern in elemento_id.lower():
                pontuacao['inscricao_fim'] += 0.5
                pontuacao['evento_fim'] += 0.5
                
        for pattern in inscricao_patterns:
            if pattern in elemento_classe.lower() or pattern in elemento_id.lower():
                pontuacao['inscricao_inicio'] += 0.3
                pontuacao['inscricao_fim'] += 0.3
                
        for pattern in evento_patterns:
            if pattern in elemento_classe.lower() or pattern in elemento_id.lower():
                pontuacao['evento_inicio'] += 0.3
                pontuacao['evento_fim'] += 0.3
    
    # 3. Análise temporal
    try:
        data = datetime.strptime(data_str, '%d/%m/%Y')
        hoje = datetime.now()
        
        # Se a data é muito próxima (próximos 30 dias), mais provável ser início
        dias_ate_data = (data - hoje).days
        if 0 <= dias_ate_data <= 30:
            pontuacao['inscricao_inicio'] += 0.3
            pontuacao['evento_inicio'] += 0.3
            
        # Se a data é mais distante (mais de 60 dias), mais provável ser fim
        elif dias_ate_data > 60:
            pontuacao['inscricao_fim'] += 0.2
            pontuacao['evento_fim'] += 0.2
            
        # Se tem posição na sequência de datas encontradas
        if posicao_na_sequencia is not None:
            if posicao_na_sequencia == 0:
                pontuacao['inscricao_inicio'] += 0.4
            elif posicao_na_sequencia == 1:
                pontuacao['inscricao_fim'] += 0.4
            elif posicao_na_sequencia == 2:
                pontuacao['evento_inicio'] += 0.4
            elif posicao_na_sequencia == 3:
                pontuacao['evento_fim'] += 0.4
    except:
        pass
    
    # 4. Análise de proximidade de outras palavras-chave
    palavras_chave = {
        'inscricao_inicio': ['abertura', 'início', 'começa', 'primeira fase', 'primeira etapa'],
        'inscricao_fim': ['encerramento', 'término', 'fecha', 'última fase', 'última etapa'],
        'evento_inicio': ['abertura do evento', 'cerimônia de abertura', 'primeiro dia'],
        'evento_fim': ['encerramento do evento', 'cerimônia de encerramento', 'último dia']
    }
    
    for tipo, palavras in palavras_chave.items():
        for palavra in palavras:
            if palavra in texto_contexto:
                pontuacao[tipo] += 0.2
    
    # Encontra o tipo com maior pontuação
    tipo_mais_provavel = max(pontuacao.items(), key=lambda x: x[1])
    
    # Retorna o tipo apenas se tiver uma pontuação mínima
    return tipo_mais_provavel[0] if tipo_mais_provavel[1] > 0.5 else None

def ordenar_datas_evento(datas_importantes):
    """
    Ordena as datas do evento para garantir que início seja antes do fim
    """
    tipos_data = ['inscricao_inicio', 'inscricao_fim', 'evento_inicio', 'evento_fim']
    datas = {}
    
    # Converte as datas para objetos datetime
    for tipo in tipos_data:
        data_str = datas_importantes[tipo]
        if data_str != 'Não encontrado':
            try:
                datas[tipo] = datetime.strptime(data_str, '%d/%m/%Y')
            except:
                continue
    
    # Verifica e corrige a ordem das datas
    if len(datas) >= 2:
        # Inscrições
        if 'inscricao_inicio' in datas and 'inscricao_fim' in datas:
            if datas['inscricao_inicio'] > datas['inscricao_fim']:
                datas_importantes['inscricao_inicio'], datas_importantes['inscricao_fim'] = \
                    datas_importantes['inscricao_fim'], datas_importantes['inscricao_inicio']
                
        # Evento
        if 'evento_inicio' in datas and 'evento_fim' in datas:
            if datas['evento_inicio'] > datas['evento_fim']:
                datas_importantes['evento_inicio'], datas_importantes['evento_fim'] = \
                    datas_importantes['evento_fim'], datas_importantes['evento_inicio']
                    
        # Garante que o evento não começa antes das inscrições terminarem
        if 'inscricao_fim' in datas and 'evento_inicio' in datas:
            if datas['evento_inicio'] < datas['inscricao_fim']:
                # Troca as datas se parecer que foram classificadas errado
                datas_importantes['inscricao_fim'], datas_importantes['evento_inicio'] = \
                    datas_importantes['evento_inicio'], datas_importantes['inscricao_fim']
    
    return datas_importantes

# --- Função Principal de Extração ---

def extrair_informacoes(url):
    """
    Acessa uma única URL e extrai as informações desejadas.
    Esta é a função que você mais vai precisar adaptar.
    """
    print(f"Processando: {url}")
    dados = {
        'url': url,
        'nome_olimpiada': 'Não encontrado',
        'datas_importantes': {
            'inscricao_inicio': 'Não encontrado',
            'inscricao_fim': 'Não encontrado',
            'evento_inicio': 'Não encontrado',
            'evento_fim': 'Não encontrado'
        },
        'documentos_inscricao': 'Não encontrado',
        'edital': 'Não encontrado'
    }

    try:
        # Ignora verificação SSL para sites problemáticos
        response = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Nome da Olimpíada/Feira - extração robusta
        def _clean_text(t):
            return ' '.join(t.split()).strip() if t else ''

        nome_encontrado = False

        # 1) Tenta meta property og:title
        meta_og = soup.find('meta', property='og:title') or soup.find('meta', attrs={'name': 'og:title'})
        if meta_og and meta_og.get('content'):
            dados['nome_olimpiada'] = _clean_text(meta_og.get('content'))
            nome_encontrado = True

        # 2) Se não, tenta <title>
        if not nome_encontrado and soup.title and soup.title.string:
            titulo_text = _clean_text(soup.title.string)
            if titulo_text:
                dados['nome_olimpiada'] = titulo_text
                nome_encontrado = True

        # 3) Se ainda não, procura <h1> com palavras-chave
        if not nome_encontrado:
            h1s = soup.find_all('h1')
            for h in h1s:
                texto = _clean_text(h.get_text(separator=' ', strip=True))
                if texto:
                    # aceita se tiver palavras-chave ou for curto e descritivo
                    if re.search(r'\b(feira|mostra|olimp[ií]ada|ci[eê]ncia|ci[eê]ncias|mostratec|febrace|femic|febic)\b', texto, re.IGNORECASE) or (5 < len(texto) < 120):
                        dados['nome_olimpiada'] = texto
                        nome_encontrado = True
                        break

        # 4) Procura por elementos com classes/ids relevantes e escolhe candidato curto
        if not nome_encontrado:
            candidato = None
            for elem in soup.find_all(True):
                # verifica classe e id
                cls_list = elem.get('class') or []
                cls = ' '.join(cls_list)
                elem_id = elem.get('id') or ''
                if re.search(r'title|heading|nome|event|feira|mostra|name|titulo|site-name|site-title|logo-text', cls + ' ' + elem_id, re.IGNORECASE):
                    texto = _clean_text(elem.get_text(separator=' ', strip=True))
                    if texto and 5 < len(texto) < 160:
                        # prefere textos curtos e sem muitos quebras
                        if not candidato or len(texto) < len(candidato):
                            candidato = texto
            if candidato:
                dados['nome_olimpiada'] = candidato
                nome_encontrado = True

        # 5) fallback: heurística por domínio conhecida
        if not nome_encontrado:
            url_lower = url.lower()
            mapa_dominios = {
                'febrace': 'Feira Brasileira de Ciências e Engenharia (FEBRACE)',
                'femic': 'Feira Mineira de Iniciação Científica (FEMIC)',
                'febic': 'Feira Brasileira de Iniciação Científica (FEBIC)',
                'mostratec': 'MOSTRATEC - Mostra Internacional de Ciência e Tecnologia',
                'fenecit': 'FENECIT - Feira Nordestina de Ciência e Tecnologia'
            }
            for chave, nome_fallback in mapa_dominios.items():
                if chave in url_lower:
                    dados['nome_olimpiada'] = nome_fallback
                    nome_encontrado = True
                    break

        # se nada foi encontrado, mantém 'Não encontrado'

        # Datas Importantes
        datas = []
        datas_classificadas = {
            'inscricao_inicio': [],
            'inscricao_fim': [],
            'evento_inicio': [],
            'evento_fim': []
        }
        
        # Procura datas em elementos específicos primeiro
        elementos_data = set()  # Usa set para evitar duplicatas
        
        # Procura em elementos com títulos relevantes
        for tag in ELEMENTOS_DATA['titulo']:
            for termo in ELEMENTOS_DATA['tabela']:  # Usa os mesmos termos da tabela
                elementos = soup.find_all(tag, string=re.compile(termo, re.IGNORECASE))
                for elem in elementos:
                    # Procura em todos os elementos irmãos até encontrar outro título
                    next_elem = elem.find_next_sibling()
                    while next_elem and next_elem.name not in ELEMENTOS_DATA['titulo']:
                        elementos_data.add(next_elem)
                        next_elem = next_elem.find_next_sibling()
        
        # Procura em tabelas
        for termo in ELEMENTOS_DATA['tabela']:
            tabelas = soup.find_all('table')
            for tabela in tabelas:
                if re.search(termo, tabela.get_text(), re.IGNORECASE):
                    elementos_data.add(tabela)
                    # Adiciona cabeçalho da tabela se existir
                    header = tabela.find_previous_sibling(ELEMENTOS_DATA['titulo'])
                    if header:
                        elementos_data.add(header)
        
        # Procura em listas
        for lista_tag in ELEMENTOS_DATA['lista']:
            listas = soup.find_all(lista_tag)
            for lista in listas:
                if any(re.search(termo, lista.get_text(), re.IGNORECASE) 
                      for termo in ELEMENTOS_DATA['tabela']):  # Usa os mesmos termos da tabela
                    elementos_data.add(lista)
                    # Adiciona o título da lista se existir
                    titulo = lista.find_previous_sibling(ELEMENTOS_DATA['titulo'])
                    if titulo:
                        elementos_data.add(titulo)
        
        # Procura em divs e seções específicas
        for termo in ELEMENTOS_DATA['div']:
            # Procura por classe
            elementos = soup.find_all(class_=re.compile(termo, re.IGNORECASE))
            for elem in elementos:
                elementos_data.add(elem)
                
            # Procura por id
            elementos = soup.find_all(id=re.compile(termo, re.IGNORECASE))
            for elem in elementos:
                elementos_data.add(elem)
        
        # Procura em links específicos que podem conter datas
        for termo in ELEMENTOS_DATA['link']:
            links = soup.find_all('a', href=re.compile(termo, re.IGNORECASE))
            for link in links:
                parent = link.find_parent(['div', 'section', 'article'])
                if parent:
                    elementos_data.add(parent)
        
        # Extrai datas dos elementos específicos
        for elemento in elementos_data:
            datas_do_elemento = extrair_datas_elemento(elemento)
            if datas_do_elemento:
                # Adiciona o texto do elemento pai e dos irmãos para melhor contexto
                for data in datas_do_elemento:
                    contexto_expandido = []
                    
                    # Adiciona texto do elemento anterior se existir
                    prev_elem = elemento.find_previous_sibling()
                    if prev_elem:
                        contexto_expandido.append(prev_elem.get_text())
                    
                    # Adiciona texto do próprio elemento
                    contexto_expandido.append(data['contexto'])
                    
                    # Adiciona texto do elemento seguinte se existir
                    next_elem = elemento.find_next_sibling()
                    if next_elem:
                        contexto_expandido.append(next_elem.get_text())
                    
                    # Atualiza o contexto da data
                    data['contexto'] = ' '.join(contexto_expandido)
                
                datas.extend(datas_do_elemento)
        
        # Se não encontrou em elementos específicos, procura no texto completo
        if not datas:
            # Procura em parágrafos com palavras-chave
            paragrafos = soup.find_all(['p', 'div', 'section'])
            for p in paragrafos:
                texto = p.get_text(separator=' ', strip=True).lower()
                if any(re.search(termo, texto, re.IGNORECASE) for termo_lista in ELEMENTOS_DATA.values() for termo in termo_lista):
                    datas_do_paragrafo = extrair_datas_elemento(p)
                    if datas_do_paragrafo:
                        # Adiciona contexto dos parágrafos vizinhos
                        for data in datas_do_paragrafo:
                            contexto_expandido = []
                            
                            # Tenta pegar o parágrafo anterior
                            prev_p = p.find_previous_sibling('p')
                            if prev_p:
                                contexto_expandido.append(prev_p.get_text())
                            
                            # Adiciona o contexto atual
                            contexto_expandido.append(data['contexto'])
                            
                            # Tenta pegar o próximo parágrafo
                            next_p = p.find_next_sibling('p')
                            if next_p:
                                contexto_expandido.append(next_p.get_text())
                            
                            # Atualiza o contexto da data
                            data['contexto'] = ' '.join(contexto_expandido)
                        
                        datas.extend(datas_do_paragrafo)
        
        # Primeira passagem: coleta e filtra datas válidas
        datas_validas = []
        for data in datas:
            contexto = data['contexto']
            data_norm = data['data']
            
            # Extrai informações do elemento
            info_elemento = {
                'elemento_tipo': data.get('elemento_tipo', ''),
                'classe': data.get('classe', ''),
                'id': data.get('id', '')
            }
            
            # Verifica se é uma data válida
            try:
                data_obj = datetime.strptime(data_norm, '%d/%m/%Y')
                data_atual = datetime.now()
                
                # Se a data é do passado mas o contexto indica evento futuro, ajusta o ano
                if data_obj < data_atual:
                    texto_baixo = contexto.lower()
                    palavras_futuro = ['próximo', 'futuro', 'seguinte', 'novo', 'próxima edição']
                    anos_futuros = re.findall(r'20[2-9][0-9]', contexto)  # Anos entre 2020 e 2099
                    
                    # Se encontrou palavras que indicam futuro ou anos futuros
                    if any(palavra in texto_baixo for palavra in palavras_futuro) or anos_futuros:
                        # Se tem ano específico no contexto, usa ele
                        if anos_futuros:
                            ano_futuro = max(int(ano) for ano in anos_futuros)
                            # Ajusta a data para o ano futuro
                            data_obj = data_obj.replace(year=ano_futuro)
                            data_norm = data_obj.strftime('%d/%m/%Y')
                        else:
                            # Senão, avança para o próximo ano
                            while data_obj < data_atual:
                                data_obj = data_obj.replace(year=data_obj.year + 1)
                            data_norm = data_obj.strftime('%d/%m/%Y')
                
                # Adiciona mais informações para ajudar na classificação
                data_valida = {
                    'data': data_norm,
                    'contexto': contexto,
                    'obj': data_obj,
                    'info_elemento': info_elemento,
                    'classificacoes': {},  # Vai armazenar pontuações para cada tipo
                    'melhor_classificacao': None,
                    'pontuacao_maxima': 0
                }
                
                # Classifica a data para cada tipo possível
                for tipo in ['inscricao_inicio', 'inscricao_fim', 'evento_inicio', 'evento_fim']:
                    tipo_classificado = classificar_data(data_norm, contexto, None, info_elemento)
                    if tipo_classificado == tipo:
                        data_valida['classificacoes'][tipo] = True
                
                datas_validas.append(data_valida)
            except Exception as e:
                continue
                
        # Ordena as datas válidas
        datas_validas.sort(key=lambda x: x['obj'])
        
        # Segunda passagem: refinamento da classificação considerando a sequência temporal
        for i, data in enumerate(datas_validas):
            # Tenta classificar usando a posição na sequência como contexto adicional
            tipo_data = classificar_data(data['data'], data['contexto'], i, data['info_elemento'])
            if tipo_data and not datas_classificadas[tipo_data]:
                datas_classificadas[tipo_data].append(data['data'])
                data['melhor_classificacao'] = tipo_data
        
        # Terceira passagem: análise de padrões temporais
        if len(datas_validas) >= 2:
            # Se temos exatamente duas datas próximas (diferença < 30 dias)
            if len(datas_validas) == 2:
                data1, data2 = datas_validas[0], datas_validas[1]
                diff_dias = (data2['obj'] - data1['obj']).days
                
                if diff_dias < 30:
                    # Provavelmente são datas de inscrição
                    if not datas_classificadas['inscricao_inicio']:
                        datas_classificadas['inscricao_inicio'].append(data1['data'])
                    if not datas_classificadas['inscricao_fim']:
                        datas_classificadas['inscricao_fim'].append(data2['data'])
                else:
                    # Provavelmente uma é inscrição e outra é evento
                    if not datas_classificadas['inscricao_inicio']:
                        datas_classificadas['inscricao_inicio'].append(data1['data'])
                    if not datas_classificadas['evento_inicio']:
                        datas_classificadas['evento_inicio'].append(data2['data'])
            
            # Se temos mais de duas datas, tentamos identificar padrões
            elif len(datas_validas) > 2:
                # Agrupa datas próximas (diferença < 15 dias)
                grupos_datas = [[datas_validas[0]]]
                for data in datas_validas[1:]:
                    if (data['obj'] - grupos_datas[-1][-1]['obj']).days < 15:
                        grupos_datas[-1].append(data)
                    else:
                        grupos_datas.append([data])
                
                # Classifica grupos
                if len(grupos_datas) == 2:
                    # Primeiro grupo provavelmente é inscrição, segundo é evento
                    grupo_inscricao = grupos_datas[0]
                    grupo_evento = grupos_datas[1]
                    
                    if not datas_classificadas['inscricao_inicio'] and grupo_inscricao:
                        datas_classificadas['inscricao_inicio'].append(grupo_inscricao[0]['data'])
                    if not datas_classificadas['inscricao_fim'] and len(grupo_inscricao) > 1:
                        datas_classificadas['inscricao_fim'].append(grupo_inscricao[-1]['data'])
                    
                    if not datas_classificadas['evento_inicio'] and grupo_evento:
                        datas_classificadas['evento_inicio'].append(grupo_evento[0]['data'])
                    if not datas_classificadas['evento_fim'] and len(grupo_evento) > 1:
                        datas_classificadas['evento_fim'].append(grupo_evento[-1]['data'])
        
        # Quarta passagem: classificação das datas restantes
        for data in datas_validas:
            # Verifica se a data já foi classificada
            data_norm = data['data']
            classificada = False
            for tipo in datas_classificadas:
                if data_norm in datas_classificadas[tipo]:
                    classificada = True
                    break
            
            if not classificada:
                # Usa as classificações calculadas anteriormente
                classificacoes = data.get('classificacoes', {})
                if classificacoes:
                    for tipo in ['inscricao_inicio', 'inscricao_fim', 'evento_inicio', 'evento_fim']:
                        if classificacoes.get(tipo) and not datas_classificadas[tipo]:
                            datas_classificadas[tipo].append(data_norm)
                            classificada = True
                            break
                
                # Se ainda não foi classificada, usa a ordem padrão
                if not classificada:
                    if not datas_classificadas['inscricao_inicio']:
                        datas_classificadas['inscricao_inicio'].append(data_norm)
                    elif not datas_classificadas['inscricao_fim']:
                        datas_classificadas['inscricao_fim'].append(data_norm)
                    elif not datas_classificadas['evento_inicio']:
                        datas_classificadas['evento_inicio'].append(data_norm)
                    elif not datas_classificadas['evento_fim']:
                        datas_classificadas['evento_fim'].append(data_norm)
        
        # Atualiza o dicionário de dados com as datas encontradas e ordena
        for tipo in datas_classificadas:
            if datas_classificadas[tipo]:
                dados['datas_importantes'][tipo] = datas_classificadas[tipo][0]
                
        # Ordena as datas do evento
        dados['datas_importantes'] = ordenar_datas_evento(dados['datas_importantes'])

        # Documentos para Inscrição - procura por links de editais/regulamentos/formulários
        try:
            doc_keywords = [
                r'edital', r'regulamento', r'regras', r'inscri', r'documento', r'documenta',
                r'formul', r'formul[áa]rio', r'download', r'pdf', r'modelo', r'template', r'participa'
            ]

            candidates = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text(separator=' ', strip=True)
                href_lower = href.lower()
                score = 0
                # forte sinal para PDF direto
                if href_lower.endswith('.pdf'):
                    score += 10
                # palavras-chave no href ou no texto do link
                for kw in doc_keywords:
                    if re.search(kw, href_lower, re.IGNORECASE):
                        score += 4
                    if text and re.search(kw, text, re.IGNORECASE):
                        score += 3
                if score > 0:
                    full = urllib.parse.urljoin(url, href)
                    candidates.append((score, full, text))

            # Ordena por score desc e URL para estabilidade
            candidates = sorted(candidates, key=lambda x: (-x[0], x[1]))

            found_doc = None
            # Prioriza PDF direto
            for sc, link_url, anchor in candidates:
                if link_url.lower().endswith('.pdf'):
                    found_doc = link_url
                    break

            # Se não achou PDF, pega primeiro HTML candidato e tenta extrair PDFs/listas internos
            if not found_doc and candidates:
                # segue apenas 1 nível por segurança
                sc, link_url, anchor = candidates[0]
                try:
                    resp = requests.get(link_url, headers=HEADERS, timeout=10, verify=False)
                    resp.raise_for_status()
                    sub_soup = BeautifulSoup(resp.content, 'html.parser')
                    # procura por PDFs nessa página
                    pdf = None
                    for a in sub_soup.find_all('a', href=True):
                        href2 = a['href']
                        if href2.lower().endswith('.pdf'):
                            pdf = urllib.parse.urljoin(link_url, href2)
                            break
                    if pdf:
                        found_doc = pdf
                    else:
                        # procura por listas de documentos
                        lista = sub_soup.find('ul') or sub_soup.find('ol')
                        if lista:
                            # junta itens da lista como texto
                            found_doc = link_url + ' | ' + lista.get_text(separator='; ', strip=True)
                        else:
                            # fallback para a própria página HTML
                            found_doc = link_url
                except Exception:
                    # se falhar ao seguir, usa o href original como fallback
                    found_doc = link_url

            if found_doc:
                dados['documentos_inscricao'] = found_doc

            # se nada foi encontrado acima, mantemos o valor padrão 'Não encontrado'
        except Exception:
            # não deixar o crawler quebrar por causa dessa parte
            pass

        # Edital e Regulamento
        edital_patterns = [
            r'edital', r'regulamento', r'regras', r'instruções',
            r'manual do participante', r'orientações gerais'
        ]
        
        # Procura links com texto ou href contendo os padrões
        edital_links = []
        for pattern in edital_patterns:
            # Procura no texto do link
            links = soup.find_all('a', string=re.compile(pattern, re.IGNORECASE))
            edital_links.extend(links)
            
            # Procura no href
            links = soup.find_all('a', href=re.compile(pattern, re.IGNORECASE))
            edital_links.extend(links)
            
        if edital_links:
            editais = []
            for link in edital_links:
                href = link['href']
                if not href.startswith('http'):
                    href = urllib.parse.urljoin(url, href)
                if href.endswith(('.pdf', '.doc', '.docx', '.html', '/')):
                    editais.append(href)
            
            dados['edital'] = editais[0] if editais else 'Não encontrado'
            
        # Tratamento específico para sites conhecidos
        if 'febrace.org.br' in url:
            # Tratamento específico para FEBRACE
            regulamento = soup.find('a', string=re.compile(r'regulamento|submissão|regras', re.IGNORECASE))
            if regulamento:
                dados['edital'] = urllib.parse.urljoin(url, regulamento['href'])
            # Procura por datas em seções específicas
            cronograma = soup.find(string=re.compile(r'cronograma|calendario', re.IGNORECASE))
            if cronograma:
                texto_cronograma = cronograma.find_parent().get_text(separator='\n', strip=True)
                datas = extrair_datas_elemento(cronograma.find_parent())
                for data in datas:
                    if re.search(r'inscr|cadastr', data['contexto']):
                        if dados['datas_importantes']['inscricao_inicio'] == 'Não encontrado':
                            dados['datas_importantes']['inscricao_inicio'] = data['data']
                        elif dados['datas_importantes']['inscricao_fim'] == 'Não encontrado':
                            dados['datas_importantes']['inscricao_fim'] = data['data']
                
        elif 'femic.com.br' in url:
            # Tratamento específico para FEMIC
            regulamento = soup.find('a', string=re.compile(r'regulamento|edital|regras', re.IGNORECASE))
            if regulamento:
                dados['edital'] = urllib.parse.urljoin(url, regulamento['href'])
            # Procura por documentos necessários
            docs = soup.find(string=re.compile(r'documentação necessária|documentos obrigatórios', re.IGNORECASE))
            if docs:
                dados['documentos_inscricao'] = docs.find_parent().get_text(separator='\n', strip=True)
                
        elif 'febic.com.br' in url:
            # Tratamento específico para FEBIC
            if '#regulamento' in url:
                dados['edital'] = url
            # Procura por links de PDF que podem ser editais
            pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$'))
            for link in pdf_links:
                if re.search(r'regul|edit|manual', link.get_text(), re.IGNORECASE):
                    dados['edital'] = urllib.parse.urljoin(url, link['href'])
                    break

    except Exception as e:
        print(f"Erro ao processar a página {url}: {e}")

    return dados

# --- Execução do Crawler ---

def remover_duplicatas(df):
    """
    Remove entradas duplicadas do DataFrame, mantendo apenas a mais completa
    """
    # Ordena o DataFrame por completude (quanto menos 'Não encontrado', melhor)
    df['completude'] = df.apply(lambda row: -sum(1 for value in row if value == 'Não encontrado'), axis=1)
    df = df.sort_values('completude')
    
    # Remove duplicatas mantendo a entrada mais completa
    df = df.drop_duplicates(subset=['url'], keep='last')
    df = df.drop('completude', axis=1)
    return df

if __name__ == "__main__":
    # Tenta ler links do arquivo gerado pelo webc.py
    links_path = Path('resultados_links_crawler/links_extraidos.txt')
    latest_file = None
    
    # Procura o arquivo mais recente
    if links_path.parent.exists():
        files = list(links_path.parent.glob('links_extraidos_*.txt'))
        if files:
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
    
    if latest_file:
        with open(latest_file, 'r', encoding='utf-8') as f:
            URLS_OLIMPIADAS = [linha.strip() for linha in f if linha.strip()]
        print(f"Lendo {len(URLS_OLIMPIADAS)} URLs do arquivo {latest_file}")
    else:
        print("Arquivo de links não encontrado, usando lista padrão.")

    # Processa os resultados
    resultados = []
    for url in URLS_OLIMPIADAS:
        resultado = extrair_informacoes(url)
        resultados.append(resultado)

    # Cria o DataFrame
    df = pd.DataFrame(resultados)
    
    # Expande a coluna de datas_importantes
    datas_df = pd.DataFrame(list(df['datas_importantes']))
    df = df.drop('datas_importantes', axis=1)
    df = pd.concat([df, datas_df], axis=1)
    
    # Remove duplicatas
    df = remover_duplicatas(df)

    # Cria o diretório de resultados se não existir
    output_dir = Path('resultados_site_crawler')
    output_dir.mkdir(exist_ok=True)

    # Gera nome do arquivo com timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'dados_olimpiadas_{timestamp}.csv'

    # Salva os resultados
    df.to_csv(output_file, index=False)
    print(f'Resultados salvos em: {output_file}')

    print("\n--- Processamento Finalizado ---")
    print(f"Dados salvos com sucesso no arquivo '{output_file}'")
    print(df)