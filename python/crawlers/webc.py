# -*- coding: utf-8 -*-

import time
import urllib.parse
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime

# -----------------------------------------------------------------------------
# Documentação: Novas importações para o Selenium
# -----------------------------------------------------------------------------
# selenium.webdriver: A principal ferramenta para controlar o navegador.
# selenium.webdriver.chrome.service.Service: Para gerir o serviço do ChromeDriver.
# webdriver_manager.chrome.ChromeDriverManager: Para descarregar e instalar
#   automaticamente o "driver" correto para a sua versão do Chrome.
# By: Para encontrar elementos na página (ex: por ID, por classe, etc.).
# -----------------------------------------------------------------------------
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def buscador_de_dados_selenium(pergunta_chave):
    """
    Função que usa o Selenium para controlar um navegador Chrome,
    realizar a busca e extrair os links dos resultados.
    """
    
    termo_busca_formatado = urllib.parse.quote_plus(pergunta_chave)
    url_busca = f"https://www.google.com/search?q={termo_busca_formatado}"

    # -----------------------------------------------------------------------------
    # Documentação: Configurar e Iniciar o Navegador (Selenium)
    # -----------------------------------------------------------------------------
    # Isto configura o Selenium para descarregar e usar o driver do Chrome
    # automaticamente. Não precisa de se preocupar em descarregar nada manualmente.
    # -----------------------------------------------------------------------------
    print("🤖 Iniciando o navegador controlado por Selenium...")
    service = Service(ChromeDriverManager().install())
    
    # Configurações do navegador para evitar detecção
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(service=service, options=options)

    try:
        print(f"🔎 Navegando para o Google e buscando por: '{pergunta_chave}'...")
        driver.get(url_busca)

        # -----------------------------------------------------------------------------
        # Documentação: Esperar a Página Carregar
        # -----------------------------------------------------------------------------
        # Damos um tempo para que o JavaScript do Google execute e carregue os
        # resultados. 5 segundos é geralmente suficiente.
        # -----------------------------------------------------------------------------
        print("⏳ Esperando o JavaScript carregar os resultados...")
        time.sleep(5)

        # -----------------------------------------------------------------------------
        # Documentação: Extrair o HTML e Usar o BeautifulSoup
        # -----------------------------------------------------------------------------
        # Agora que a página está completa, pegamos o HTML (driver.page_source)
        # e entregamo-lo ao BeautifulSoup, como fazíamos antes.
        # -----------------------------------------------------------------------------
        html_completo = driver.page_source
        soup = BeautifulSoup(html_completo, 'html.parser')

        # Novo método para extrair links dos resultados do Google
        resultados = []
        # Procura por diferentes padrões de resultados do Google
        for bloco in soup.select('div.g, div[data-header-feature], div[data-hveid]'):
            try:
                # Procura links dentro do bloco de resultado
                links = bloco.find_all('a', href=True)
                for a_tag in links:
                    # Verifica se o link tem um título (h3)
                    h3_tag = a_tag.find('h3') or a_tag.find_parent('h3')
                    if h3_tag:
                        link = a_tag['href']
                        titulo = h3_tag.get_text().strip()
                        
                        # Remove parâmetros de rastreamento do Google
                        if link.startswith('/url?'):
                            try:
                                link = urllib.parse.parse_qs(link.split('?')[1])['q'][0]
                            except:
                                continue
                                
                        # Verifica se é um link válido
                        if link.startswith('http'):
                            resultados.append((titulo, link))
            except Exception as e:
                print(f"Erro ao processar um resultado: {e}")

        print(f"\n✅ Busca concluída! Encontramos {len(resultados)} links relevantes:\n")
        for i, (titulo, link) in enumerate(resultados):
            print(f"Resultado {i+1}:")
            print(f"  Título: {titulo}")
            print(f"  URL: {link}\n")

        # Salvar os links em um arquivo para uso posterior
        Path('resultados_links_crawler').mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        links_filename = f'resultados_links_crawler/links_extraidos_{timestamp}.txt'
        with open(links_filename, 'w', encoding='utf-8') as f:
            for titulo, link in resultados:
                f.write(f"{link}\n")
        print(f"Links salvos em: {links_filename}")

    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")
    finally:
        # -----------------------------------------------------------------------------
        # Documentação: Fechar o Navegador
        # -----------------------------------------------------------------------------
        # É muito importante fechar o navegador no final para não deixar
        # processos abertos.
        # -----------------------------------------------------------------------------
        print("🚪 Fechando o navegador.")
        driver.quit()

# --- Ponto de Partida do Programa ---
if __name__ == "__main__":
    pergunta = "Feiras Cientificas 2025"
    buscador_de_dados_selenium(pergunta)