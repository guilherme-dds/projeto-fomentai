# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
import re
import time
from datetime import datetime
import urllib.parse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- Funções e Padrões de Extração (Reutilizados do site_crawler.py) ---
# (A lógica de extração de dados permanece a mesma, o que muda é como obtemos o HTML)

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
        dias_semana = r'(?:segunda|terça|quarta|quinta|sexta|sábado|domingo),?\s*'
        data_str = re.sub(dias_semana, '', data_str, flags=re.IGNORECASE)
        if re.match(r'\d{2}/\d{2}/\d{2,4}', data_str):
            dia, mes, ano = data_str.split('/')
            if len(ano) == 2: ano = '20' + ano
            return f"{dia.zfill(2)}/{mes.zfill(2)}/{ano}"
        elif re.match(r'\d{2}[.-]\d{2}[.-]\d{2,4}', data_str):
            dia, mes, ano = re.split(r'[.-]', data_str)
            if len(ano) == 2: ano = '20' + ano
            return f"{dia.zfill(2)}/{mes.zfill(2)}/{ano}"
        elif re.search(r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}', data_str, re.IGNORECASE):
            partes = re.search(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})', data_str, re.IGNORECASE)
            dia, mes_str, ano = partes.groups()
            return f"{dia.zfill(2)}/{meses[mes_str.lower()]}/{ano}"
        return data_str
    except:
        return data_str

ELEMENTOS_DATA = {
    'tabela': ['cronograma', 'datas', 'calendario', 'prazos'],
    'titulo': ['h1', 'h2', 'h3', 'strong', 'b'],
    'lista': ['ul', 'ol'],
    'div': ['calendar', 'schedule', 'datas', 'info'],
    'link': ['edital', 'regulamento', 'inscricao'],
    'especifico': ['datetime', 'date', 'time']
}
PADROES_CONTEXTO = {
    'inscricao_inicio': [
        r'in[ií]cio\s+das?\s+inscri[çc][oõ]e?s',
        r'abertura\s+das?\s+inscri[çc][oõ]e?s',
        r'inscri[çc][oõ]e?s\s+(?:a partir de|começam em)',
        r'per[ií]odo\s+de\s+inscri[çc][oõ]e?s\s+de',
        r'in[ií]cio\s+das?\s+submiss[oõ]e?s',
    ],
    'inscricao_fim': [
        r'(?:fim|t[ée]rmino|encerramento)\s+das?\s+inscri[çc][oõ]e?s',
        r'inscri[çc][oõ]e?s\s+at[ée]',
        r'prazo\s+(?:final|limite)\s+(?:para|das)\s+inscri[çc][oõ]e?s',
        r'[úu]ltimo\s+dia\s+(?:para|das)\s+inscri[çc][oõ]e?s',
        r'data\s+limite\s+(?:para|das)\s+inscri[çc][oõ]e?s',
    ],
    'evento_inicio': [
        r'in[ií]cio\s+d[ao]\s+(?:feira|evento|mostra|olimp[ií]ada|apresenta[çc][oõ]e?s)',
        r'abertura\s+d[ao]\s+(?:feira|evento|mostra|olimp[ií]ada)',
        r'(?:feira|evento|mostra|olimp[ií]ada)\s+come[çc]a',
        r'cerim[ôo]nia\s+de\s+abertura',
        r'primeiro\s+dia\s+d[ao]\s+(?:feira|evento|mostra)',
        r'realiza[çc][ãa]o\s+d[ao]\s+(?:feira|evento|mostra)',
        r'data\s+d[ao]\s+(?:feira|evento|mostra)',
    ],
    'evento_fim': [
        r'(?:fim|t[ée]rmino|encerramento)\s+d[ao]\s+(?:feira|evento|mostra|olimp[ií]ada)',
        r'(?:feira|evento|mostra|olimp[ií]ada)\s+termina',
        r'cerim[ôo]nia\s+de\s+encerramento',
        r'[úu]ltimo\s+dia\s+d[ao]\s+(?:feira|evento|mostra)',
        r'(?:feira|evento|mostra)\s+vai\s+at[ée]',
        r'at[ée]\s+o\s+dia',
    ]
}
PADROES_DATA = [r'\d{2}/\d{2}/\d{2,4}', r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}']

def extrair_datas_elemento(elemento):
    datas = []
    texto = elemento.get_text(separator=' ', strip=True)
    for padrao in PADROES_DATA:
        for match in re.finditer(padrao, texto, re.IGNORECASE):
            data = match.group()
            contexto = texto[max(0, match.start() - 50):min(len(texto), match.end() + 50)].lower()
            datas.append({'data': normalizar_data(data), 'contexto': contexto})
    return datas

def classificar_data(data_info):
    contexto = data_info['contexto']
    for tipo, padroes in PADROES_CONTEXTO.items():
        for padrao in padroes:
            if re.search(padrao, contexto, re.IGNORECASE):
                return tipo
    return None

# --- Função Principal de Extração Adaptada para Playwright ---

def extrair_informacoes_playwright(page, url):
    """
    Acessa uma única URL com Playwright e extrai as informações desejadas.
    """
    print(f"Processando com Playwright: {url}")
    dados = {
        'url': url,
        'nome_olimpiada': 'Não encontrado',
        'inscricao_inicio': 'Não encontrado',
        'inscricao_fim': 'Não encontrado',
        'evento_inicio': 'Não encontrado',
        'evento_fim': 'Não encontrado',
        'documentos_inscricao': 'Não encontrado',
        'edital': 'Não encontrado'
    }

    try:
        # Navega até a URL
        page.goto(url, timeout=60000, wait_until='domcontentloaded')
        # Espera um pouco para JS carregar, se necessário
        time.sleep(3) 
        
        # Obtém o conteúdo da página e usa o BeautifulSoup para o parsing
        html_content = page.content()
        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. Nome da Olimpíada/Feira (lógica idêntica ao site_crawler.py)
        nome_encontrado = False
        meta_og = soup.find('meta', property='og:title')
        if meta_og and meta_og.get('content'):
            dados['nome_olimpiada'] = meta_og['content'].strip()
            nome_encontrado = True
        if not nome_encontrado and soup.title and soup.title.string:
            dados['nome_olimpiada'] = soup.title.string.strip()
            nome_encontrado = True
        if not nome_encontrado:
            h1 = soup.find('h1')
            if h1:
                dados['nome_olimpiada'] = h1.get_text(strip=True)

        # 2. Datas Importantes (lógica idêntica ao site_crawler.py)
        datas_encontradas = []
        for seletor_tipo, termos in ELEMENTOS_DATA.items():
            for termo in termos:
                elementos = soup.find_all(lambda tag: termo in tag.get_text(separator=' ', strip=True).lower() or termo in str(tag.attrs).lower())
                for elem in elementos:
                    datas_encontradas.extend(extrair_datas_elemento(elem))
        
        if not datas_encontradas:
             datas_encontradas.extend(extrair_datas_elemento(soup))

        datas_classificadas = {}
        for data_info in datas_encontradas:
            tipo = classificar_data(data_info)
            if tipo and tipo not in datas_classificadas:
                datas_classificadas[tipo] = data_info['data']
        
        dados.update(datas_classificadas)

        # 3. Documentos e Edital (lógica idêntica ao site_crawler.py)
        doc_keywords = [r'edital', r'regulamento', r'regras', r'inscri', r'documento', r'formul[áa]rio', r'pdf']
        links_docs = []
        for a in soup.find_all('a', href=True):
            for kw in doc_keywords:
                if re.search(kw, a.get_text(strip=True), re.IGNORECASE) or re.search(kw, a['href'], re.IGNORECASE):
                    full_url = urllib.parse.urljoin(url, a['href'])
                    links_docs.append(full_url)
                    break # Evita adicionar o mesmo link várias vezes
        
        if links_docs:
            dados['documentos_inscricao'] = links_docs[0]
            # Heurística simples: se encontrar "edital" ou "regulamento", prioriza
            for link in links_docs:
                if 'edital' in link.lower() or 'regulamento' in link.lower():
                    dados['edital'] = link
                    break
            if dados['edital'] == 'Não encontrado':
                dados['edital'] = links_docs[0]


    except PlaywrightTimeoutError:
        print(f"Timeout ao carregar a página {url}. Pulando.")
    except Exception as e:
        print(f"Erro ao processar a página {url}: {e}")

    return dados

# --- Execução do Crawler ---

def main():
    # Tenta ler links do arquivo gerado pelo crawler de busca
    links_path = Path('resultados_links_crawler')
    latest_file = None
    
    if links_path.exists():
        files = list(links_path.glob('links_extraidos_*.txt'))
        if files:
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
    
    if latest_file:
        with open(latest_file, 'r', encoding='utf-8') as f:
            urls_para_processar = [linha.strip() for linha in f if linha.strip()]
        print(f"Lendo {len(urls_para_processar)} URLs do arquivo {latest_file.name}")
    else:
        print("Nenhum arquivo de links encontrado em 'resultados_links_crawler'. Encerrando.")
        return

    resultados = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = context.new_page()

        for url in urls_para_processar:
            resultado = extrair_informacoes_playwright(page, url)
            resultados.append(resultado)
            time.sleep(1) # Pausa para não sobrecarregar os servidores

        browser.close()

    # Cria o DataFrame e salva os resultados
    df = pd.DataFrame(resultados)
    
    # Remove duplicatas (se houver)
    df = df.drop_duplicates(subset=['url'], keep='last')

    output_dir = Path('resultados_site_crawler')
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'dados_olimpiadas_playwright_{timestamp}.csv'

    df.to_csv(output_file, index=False)
    print(f'\n--- Processamento Finalizado ---\n')
    print(f"Resultados salvos em: {output_file}")
    print(df.head())

if __name__ == "__main__":
    main()
