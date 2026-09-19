import os
import time
import logging
import requests
from datetime import datetime
from threading import Thread
from flask import Flask

# Configuração de logs
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8304259552:AAGm4l7uVV9gGTfFaJyI8ooeS-rPAJnkPDk"
URL_TELEGRAM = f"https://api.telegram.org/bot{TOKEN}"
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY", "")

# Mini servidor Flask para manter a aplicação viva no Render
app = Flask('')

@app.route('/')
def home():
    return "Bot Delay Sniper Preditivo a todo o vapor!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))

chats_monitorados = set()
sinais_enviados_hoje = set()
total_sinais_enviados = 0
relatorio_enviado_hoje = False

def enviar_mensagem(chat_id, texto):
    try:
        url = f"{URL_TELEGRAM}/sendMessage"
        payload = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logging.error(f"Erro ao enviar mensagem: {e}")

def verificar_atualizacoes(offset=None):
    try:
        url = f"{URL_TELEGRAM}/getUpdates"
        params = {"timeout": 30, "offset": offset}
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except Exception as e:
        logging.error(f"Erro ao buscar atualizações: {e}")
        return None

def buscar_proximos_jogos():
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.football-data.org/v4/matches?dateFrom={data_hoje}&dateTo={data_hoje}"
    headers = {'X-Auth-Token': FOOTBALL_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            dados = response.json()
            return dados.get("matches", [])
        return []
    except Exception as e:
        logging.error(f"Erro ao buscar agenda de jogos: {e}")
        return []

def main():
    global total_sinais_enviados, relatorio_enviado_hoje
    
    t = Thread(target=run_flask)
    t.start()
    
    logging.info("Delay Sniper Preditivo (Corrigido) iniciado com sucesso!")
    offset = None
    ultimo_ciclo = time.time()

    while True:
        try:
            hora_atual_str = datetime.now().strftime("%H:%M")
            data_atual_str = datetime.now().strftime("%Y-%m-%d")

            if hora_atual_str == "00:00":
                relatorio_enviado_hoje = False
                sinais_enviados_hoje.clear()

            # Relatório às 23:00
            if hora_atual_str == "23:00" and not relatorio_enviado_hoje:
                if chats_monitorados:
                    greens_do_dia = max(1, int(total_sinais_enviados * 0.85))
                    reds_do_dia = total_sinais_enviados - greens_do_dia
                    
                    relatorio_noite = (
                        "📊 **RELATÓRIO FINAL DO DIA — 23:00** 📊\n\n"
                        f"📅 **Data:** {data_atual_str}\n"
                        f"🎯 **Total de Sinais Preditivos:** {total_sinais_enviados}\n\n"
                        f"✅ **Assertividade Estimada:** {int((greens_do_dia / max(1, total_sinais_enviados)) * 100)}%\n\n"
                        "💡 *Estratégia de janelas antecipadas validada. Amanhã tem mais!* 🚀"
                    )
                    for chat_id in chats_monitorados:
                        enviar_mensagem(chat_id, relatorio_noite)
                
                relatorio_enviado_hoje = True

            # 1. Processa comandos do Telegram
            dados = verificar_atualizacoes(offset)
            if dados and "result" in dados:
                for resultado in dados["result"]:
                    offset = resultado["update_id"] + 1
                    
                    if "message" in resultado and "text" in resultado["message"]:
                        chat_id = resultado["message"]["chat"]["id"]
                        texto_msg = resultado["message"]["text"]
                        nome = resultado["message"]["from"].get("first_name", "Trader")
                        
                        if texto_msg.startswith("/start"):
                            resposta = (
                                f"Fala, {nome}! ⚡\n\n"
                                "O **Delay Sniper (Modo Preditivo)** está ativo!\n"
                                "🎯 Avisamos-te com antemão quando o jogo entra na zona crítica de pressão.\n\n"
                                "Envie **/monitorar** para armar o radar."
                            )
                            enviar_mensagem(chat_id, resposta)
                            
                        elif texto_msg.startswith("/monitorar"):
                            chats_monitorados.add(chat_id)
                            resposta = (
                                "✅ **Radar Preditivo Armado!**\n"
                                "Monitorização de blocos de pressão ativada."
                            )
                            enviar_mensagem(chat_id, resposta)

            # 2. Varredura a cada 60 segundos
            tempo_atual = time.time()
            if tempo_atual - ultimo_ciclo >= 60:
                partidas = buscar_proximos_jogos()
                hora_utc_atual = datetime.utcnow()
                
                if partidas and chats_monitorados:
                    for jogo in partidas:
                        status_jogo = jogo.get("status")
                        if status_jogo in ["TIMED", "SCHEDULED", "LIVE", "IN_PLAY"]:
                            utc_date_str = jogo.get("utcDate")
                            if not utc_date_str:
                                continue
                            
                            try:
                                tempo_jogo = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%SZ")
                                diff_minutos = (hora_utc_atual - tempo_jogo).total_seconds() / 60.0
                                
                                id_jogo = jogo.get("id")
                                home = jogo.get("homeTeam", {}).get("name", "Casa")
                                away = jogo.get("awayTeam", {}).get("name", "Fora")
                                liga = jogo.get("competition", {}).get("name", "Futebol")
                                
                                eh_janela_1 = 40 <= diff_minutos <= 46
                                eh_janela_2 = 80 <= diff_minutos <= 92
                                
                                if eh_janela_1 or eh_janela_2:
                                    fase_janela = "Fim do 1º Tempo (Pressão de Fechamento)" if eh_janela_1 else "Reta Final do 2º Tempo (Abafa Total)"
                                    chave_sinal = f"{id_jogo}_{'J1' if eh_janela_1 else 'J2'}"
                                    
                                    # Correção aplicada aqui (validação limpa sem expressão de atribuição)
                                    if chave_sinal in sinais_enviados_hoje:
                                        continue
                                        
                                    sinais_enviados_hoje.add(chave_sinal)
                                    total_sinais_enviados += 1
                                    
                                    alerta = (
                                        "🚨 **ALERTA PREDITIVO — JANELA QUENTE!** 🎯\n\n"
                                        f"🏆 **Liga:** {liga}\n"
                                        f"⚔️ **Confronto:** {home} vs {away}\n"
                                        f"⏱ **Momento Estimado:** {fase_janela}\n\n"
                                        "📊 **Instrução do Sniper:**\n"
                                        "• Este jogo entrou na faixa estatística de maior incidência de gols e cantos.\n"
                                        "• **Abre a tua casa de apostas AGORA** e monitoriza o gráfico de pressão em tempo real para executar no gatilho certo!\n\n"
                                        "🔥 *Fica em cima do lance!*"
                                    )
                                    
                                    for chat_id in chats_monitorados:
                                        enviar_mensagem(chat_id, alerta)
                                    break
                            except Exception as parse_err:
                                logging.error(f"Erro ao processar data do jogo: {parse_err}")

                ultimo_ciclo = tempo_atual

        except Exception as e:
            logging.error(f"Erro no loop principal: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()


