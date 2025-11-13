# -*- coding: utf-8 -*-

import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
from flask import Flask, request, jsonify
import json
import time

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configurar a API do Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("A chave da API do Gemini não foi encontrada. Verifique seu arquivo .env.")

genai.configure(api_key=api_key)

def encontrar_csv_mais_recente(diretorio):
    """Encontra o arquivo CSV mais recente em um diretório."""
    diretorio_path = Path(diretorio)
    arquivos_csv = list(diretorio_path.glob('*.csv'))
    if not arquivos_csv:
        return None
    arquivo_mais_recente = max(arquivos_csv, key=lambda f: f.stat().st_mtime)
    return arquivo_mais_recente

def analisar_relevancia_projeto_lote(descricao_projeto, lista_feiras_json):
    """
    Usa a API do Gemini para analisar um projeto contra uma lista de feiras em uma única chamada.
    """
    # Usando um modelo mais recente e capaz de lidar com JSON e instruções complexas
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Configuração para garantir que a saída seja JSON
    generation_config = {
        "response_mime_type": "application/json",
    }

    prompt = f"""
    Você é um especialista em feiras científicas. Analise a relevância do projeto descrito abaixo para cada uma das feiras na lista JSON fornecida.

    **Descrição do Projeto:**
    {descricao_projeto}

    **Lista de Feiras (JSON):**
    {lista_feiras_json}

    **Instruções de Saída:**
    Retorne um objeto JSON contendo uma chave "analises". O valor dessa chave deve ser um array de objetos, um para cada feira.
    Cada objeto deve ter duas chaves:
    - "url": A URL original da feira.
    - "analise_formatada": Uma string contendo a análise no formato exato abaixo.

    **Formato para a string "analise_formatada":**
*Resposta:* [Sim, Não ou Talvez]
*Justificativa:* [Explique brevemente o motivo da sua resposta, destacando como as características do projeto se alinham (ou não) com o perfil da feira.]

    **Exemplo de formato de saída JSON:**
    {{
      "analises": [
        {{ "url": "http://exemplo.com/feira1", "analise_formatada": "*Resposta:* Sim\n*Justificativa:* O projeto se alinha perfeitamente com o foco em tecnologia da feira." }},
        {{ "url": "http://exemplo.com/feira2", "analise_formatada": "*Resposta:* Não\n*Justificativa:* O tema do projeto está fora do escopo de ciências humanas desta feira." }}
      ]
    }}
    """

    try:
        # Aumentando o timeout pois a tarefa é maior
        response = model.generate_content(prompt, generation_config=generation_config, request_options={"timeout": 300})
        return json.loads(response.text)
    except Exception as e:
        print(f"Erro na API do Gemini: {e}")
        return {"erro": f"Erro ao analisar com a API do Gemini: {e}"}

@app.route("/analisar", methods=['POST'])
def analisar_projeto():
    data = request.get_json()
    if not data or 'description' not in data:
        return jsonify({"erro": "A descrição do projeto é obrigatória."}), 400
    
    project_description = data['description']

    # Constrói o caminho absoluto para a pasta de resultados
    script_dir = Path(__file__).parent
    diretorio_resultados = script_dir.parent / 'resultados_site_crawler'
    arquivo_csv = encontrar_csv_mais_recente(diretorio_resultados)

    if not arquivo_csv:
        error_msg = f"Nenhum arquivo CSV de feiras encontrado em '{diretorio_resultados}'."
        return jsonify({"erro": error_msg}), 404

    try:
        df_feiras = pd.read_csv(arquivo_csv)
        df_feiras = df_feiras.fillna('')
    except Exception as e:
        error_msg = f"Erro ao ler o arquivo CSV de feiras: {e}"
        return jsonify({"erro": error_msg}), 500

    # Otimização: Selecionar apenas as colunas relevantes para a análise
    colunas_relevantes = ['url', 'nome_olimpiada', 'inscricao_inicio', 'inscricao_fim', 'evento_inicio', 'evento_fim']
    # Garantir que todas as colunas existam no DataFrame
    colunas_existentes = [col for col in colunas_relevantes if col in df_feiras.columns]
    df_resumido = df_feiras[colunas_existentes]

    # Converter o DataFrame resumido para um formato JSON para enviar à IA
    lista_feiras_json = df_resumido.to_json(orient='records', indent=4)

    # --- Chamada Única para a API ---
    print("Enviando lote de feiras para análise do Gemini...")
    resultado_lote = analisar_relevancia_projeto_lote(project_description, lista_feiras_json)

    if "erro" in resultado_lote:
        return jsonify(resultado_lote), 500

    # Mapear os resultados da IA de volta para os dados completos das feiras
    mapa_analises = {analise['url']: analise for analise in resultado_lote.get('analises', [])}
    
    resultados_finais = []
    for _, feira_completa in df_feiras.iterrows():
        url_feira = feira_completa['url']
        analise_ia = mapa_analises.get(url_feira)
        
        if analise_ia and 'analise_formatada' in analise_ia:
            # Constrói a string de análise final no formato solicitado
            texto_analise_final = (
                f"Resultado da Análise:\n{analise_ia['analise_formatada']}"
            )
            
            # Cria o objeto simplificado para a resposta final
            resultados_finais.append({
                "URL da feira": url_feira,
                "Justificativa": texto_analise_final
            })

    return jsonify(resultados_finais)

if __name__ == "__main__":
    # O modo debug permite que o servidor reinicie automaticamente após alterações no código.
    # Não use debug=True em um ambiente de produção.
    app.run(host="0.0.0.0", port=8000, debug=True)
