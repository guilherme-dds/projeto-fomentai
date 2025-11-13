# -*- coding: utf-8 -*-

import time
import urllib.parse
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def buscador_de_links_playwright(pergunta_chave, headless=True):
    """
    Função que usa o Playwright para controlar um navegador,
    realizar a busca no Google e extrair os links dos resultados.
    """
    
    termo_busca_formatado = urllib.parse.quote_plus(pergunta_chave)
    url_busca = f"https://www.google.com/search?q={termo_busca_formatado}"

    resultados = []

    with sync_playwright() as p:
        print("🤖 Iniciando o navegador controlado por Playwright...")
        browser = p.chromium.launch(headless=headless)
        
        # Usar um contexto de navegador que simula um dispositivo comum
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = context.new_page()

        try:
            print(f"🔎 Navegando para o Google e buscando por: '{pergunta_chave}'...")
            page.goto(url_busca, timeout=60000)

            # Tenta aceitar o pop-up de cookies se ele aparecer
            try:
                # Google usa diferentes seletores, vamos tentar alguns comuns
                cookie_button_selectors = [
                    "button:has-text('Accept all')",
                    "button:has-text('Aceitar tudo')",
                    "button:has-text('I agree')",
                    "div[role='button']:has-text('Aceito')"
                ]
                
                for selector in cookie_button_selectors:
                    button = page.query_selector(selector)
                    if button:
                        print("🍪 Aceitando o pop-up de cookies...")
                        button.click()
                        time.sleep(1) # Pequena pausa para a página reagir
                        break
            except PlaywrightTimeoutError:
                print("Pop-up de cookies não encontrado ou não foi necessário clicar.")
            except Exception as e:
                print(f"Ocorreu um erro ao tentar aceitar cookies: {e}")


            print("⏳ Esperando a página carregar os resultados...")
            # Espera que os blocos de resultados de busca estejam visíveis
            page.wait_for_selector('div[data-hveid]', timeout=15000)

            print("✅ Página carregada. Extraindo links...")
            
            # Extrai os links dos resultados da busca
            # O seletor 'div.g' é um dos mais comuns para blocos de resultado
            # Dentro de cada bloco, procuramos por um link que tenha um  H3
            links_encontrados = page.query_selector_all('div.g a')

            for link_element in links_encontrados:
                href = link_element.get_attribute('href')
                h3 = link_element.query_selector('h3')

                if href and h3:
                    titulo = h3.inner_text()
                    
                    # Limpa o link se for um redirecionamento do Google
                    if href.startswith('/url?'):
                        try:
                            parsed_url = urllib.parse.urlparse(href)
                            link_real = urllib.parse.parse_qs(parsed_url.query)['q'][0]
                        except (KeyError, IndexError):
                            continue # Pula se não conseguir extrair o link real
                    else:
                        link_real = href

                    # Garante que é um link válido e não duplicado
                    if link_real.startswith('http') and (titulo, link_real) not in resultados:
                        resultados.append((titulo, link_real))

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
                for _, link in resultados:
                    f.write(f"{link}\n")
            print(f"Links salvos em: {links_filename}")

        except PlaywrightTimeoutError:
            print("❌ O tempo de espera para carregar a página foi excedido. O Google pode estar bloqueando o acesso.")
        except Exception as e:
            print(f"❌ Ocorreu um erro inesperado: {e}")
        finally:
            print("🚪 Fechando o navegador.")
            browser.close()

# --- Ponto de Partida do Programa ---
if __name__ == "__main__":
    pergunta = "Feiras Cientificas 2025"
    # Mude para headless=False para ver o navegador em ação
    buscador_de_links_playwright(pergunta, headless=True)
