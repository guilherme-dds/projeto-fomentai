import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time

load_dotenv()

app = Flask(__name__)
CORS(app)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("A chave da API do Gemini não foi encontrada. Verifique seu arquivo .env.")

genai.configure(api_key=api_key)

def encontrar_csv_mais_recente(diretorio):
    diretorio_path = Path(diretorio)
    arquivos_csv = list(diretorio_path.glob('*.csv'))
    if not arquivos_csv:
        return None
    arquivo_mais_recente = max(arquivos_csv, key=lambda f: f.stat().st_mtime)
    return arquivo_mais_recente

def analisar_relevancia_projeto_lote(descricao_projeto, lista_feiras_json):
    model = genai.GenerativeModel('gemini-2.0-flash')

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
        response = model.generate_content(prompt, generation_config=generation_config, request_options={"timeout": 300})
        if not response.text:
            print("Erro na API do Gemini: Resposta vazia recebida.")
            return {"erro": "A API de análise retornou uma resposta vazia."}
        
        return json.loads(response.text)
    except json.JSONDecodeError:
        print(f"Erro de decodificação JSON da resposta da API: {response.text}")
        return {"erro": "A API de análise retornou um formato de dados inválido."}
    except Exception as e:
        print(f"Erro genérico na API do Gemini: {e}")
        return {"erro": f"Erro ao analisar com a API do Gemini: {e}"}

@app.route("/analisar", methods=['POST'])
def analisar_projeto():
    data = request.get_json()
    if not data or 'description' not in data:
        return jsonify({"erro": "A descrição do projeto é obrigatória."}), 400
    
    project_description = data['description']

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

    colunas_relevantes = ['url', 'nome_olimpiada', 'inscricao_inicio', 'inscricao_fim', 'evento_inicio', 'evento_fim']
    colunas_existentes = [col for col in colunas_relevantes if col in df_feiras.columns]
    df_resumido = df_feiras[colunas_existentes]

    lista_feiras_json = df_resumido.to_json(orient='records', indent=4)

    print("Enviando lote de feiras para análise do Gemini...")
    resultado_lote = analisar_relevancia_projeto_lote(project_description, lista_feiras_json)

    if "erro" in resultado_lote:
        return jsonify(resultado_lote), 500

    mapa_analises = {analise['url']: analise for analise in resultado_lote.get('analises', [])}
    
    resultados_finais = []
    for _, feira_completa in df_feiras.iterrows():
        url_feira = feira_completa.get('url')
        if not url_feira:
            continue
        analise_ia = mapa_analises.get(url_feira)
        
        if analise_ia and 'analise_formatada' in analise_ia:            
            analise_str = analise_ia['analise_formatada']
            resposta = "Não informado"
            justificativa = "Não informado"

            for linha in analise_str.split('\n'):
                if '*Resposta:*' in linha:
                    resposta = linha.split('*Resposta:*', 1)[1].strip()
                elif '*Justificativa:*' in linha:
                    justificativa = linha.split('*Justificativa:*', 1)[1].strip()
            
            resultados_finais.append({
                "nome_feira": feira_completa.get('nome_olimpiada', 'Nome não disponível'),
                "url_feira": url_feira,
                "resposta": resposta,
                "justificativa": justificativa
            })

    return jsonify(resultados_finais)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
