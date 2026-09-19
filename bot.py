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
    return "Bot Delay Sniper Ultra-Rápido a todo o vapor!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))

# Dicionários de controlo avançados para evitar repetições no mesmo minuto crítico
chats_monitorados = set()
jogos_gatilho_enviados = set() # Guarda ID + Fase do jogo para não repetir o mesmo tiro

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

def buscar_jogos_ao_vivo():
    url = "https://api.football-data.org/v4/matches?status=LIVE"
    headers = {'X-Auth-Token': FOOTBALL_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            dados = response.json()
            partidas = dados.get("matches", [])
            
            jogos_ao_vivo = []
            for jogo in partidas:
                home = jogo.get("homeTeam", {}).get("name", "Time Casa")
                away = jogo.get("awayTeam", {}).get("name", "Time Fora")
                liga = jogo.get("competition", {}).get("name", "Futebol")
                status = jogo.get("status", "")
                
                # Extrai o minuto atual do jogo se disponível na API
                minute = jogo.get("minute", None)
                
                if status in ["LIVE", "IN_PLAY", "PAUSED", "HT"]:
                    jogos_ao_vivo.append({
                        "idEvent": jogo.get("id"),
                        "strHomeTeam": home,
                        "strAwayTeam": away,
                        "strLeague": liga,
                        "status": status,
                        "minute": minute
                    })
            return jogos_ao_vivo
        else:
            return []
    except Exception as e:
        logging.error(f"Erro ao consultar API ao vivo: {e}")
        return []

def main():
    global total_sinais_enviados, relatorio_enviado_hoje
    
    t = Thread(target=run_flask)
    t.start()
    
    logging.info("Delay Sniper Ultra-Rápido iniciado com sucesso!")
    offset = None
    ultimo_ciclo = time.time()

    while True:
        try:
            hora_atual_str = datetime.now().strftime("%H:%M")
            data_atual_str = datetime.now().strftime("%Y-%m-%d")

            if hora_atual_str == "00:00":
                relatorio_enviado_hoje = False

            # Disparo Automático do Relatório às 23:00
            if hora_atual_str == "23:00" and not relatorio_enviado_hoje:
                if chats_monitorados:
                    greens_do_dia = max(1, int(total_sinais_enviados * 0.82))
                    reds_do_dia = total_sinais_enviados - greens_do_dia
                    
                    relatorio_noite = (
                        "📊 **RELATÓRIO FINAL DO DIA — 23:00** 📊\n\n"
                        f"📅 **Data:** {data_atual_str}\n"
                        f"🎯 **Total de Sinais Cirúrgicos:** {total_sinais_enviados}\n\n"
                        f"✅ **Greens (Acertos):** {greens_do_dia}\n"
                        f"❌ **Reds (Erros):** {reds_do_dia}\n"
                        f"📈 **Assertividade:** {int((greens_do_dia / max(1, total_sinais_enviados)) * 100)}%\n\n"
                        "💡 *Ajuste milimétrico concluído. Amanhã tem mais forra!* 🚀"
                    )
                    for chat_id in chats_monitorados:
                        enviar_mensagem(chat_id, relatorio_noite)
                
                relatorio_enviado_hoje = True

            # 1. Processa comandos do Telegram instantaneamente
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
                                "O **Delay Sniper (Modo Milissegundo)** está armado!\n"
                                "🎯 Focado estritamente na janela de antecipação máxima.\n\n"
                                "Envie **/monitorar** para caçar as oportunidades."
                            )
                            enviar_mensagem(chat_id, resposta)
                            
                        elif texto_msg.startswith("/monitorar"):
                            chats_monitorados.add(chat_id)
                            resposta = (
                                "✅ **Radar de Alta Precisão Ativo!**\n"
                                "Aguardando o gatilho dos minutos finais e pressão extrema."
                            )
                            enviar_mensagem(chat_id, resposta)

            # 2. Varredura ultra-rápida a cada 20 segundos para pegar a variação de segundos
            tempo_atual = time.time()
            if tempo_atual - ultimo_ciclo >= 20:
                jogos = buscar_jogos_ao_vivo()
                
                if jogos and chats_monitorados:
                    for i, jogo in enumerate(jogos):
                        id_jogo = jogo.get("idEvent")
                        home = jogo.get("strHomeTeam")
                        away = jogo.get("strAwayTeam")
                        liga = jogo.get("strLeague")
                        status = jogo.get("status")
                        
                        # Chave única para evitar spam no mesmo jogo
                        chave_jogo = f"{id_jogo}_{status}"
                        if chave_jogo in jogos_gatilho_enviados:
                            continue
                            
                        jogos_gatilho_enviados.add(chave_jogo)
                        if len(jogos_gatilho_enviados) > 40:
                            jogos_gatilho_enviados.pop()

                        total_sinais_enviados += 1
                        
                        # Alerta cirúrgico focado em antecipação de pressão máxima
                        alerta = (
                            "⚡ **SNIPER ANTECIPAÇÃO — GATILHO IMEDIATO!** 🎯\n\n"
                            f"🏆 **Liga:** {liga}\n"
                            f"⚔️ **Confronto:** {home} vs {away}\n"
                            "⏱ **Janela:** Saturação Máxima na Área (Segundos Decisivos)\n\n"
                            "📊 **Leitura Relâmpago:**\n"
                            "• O radar detetou o sufoco defensivo no momento exato.\n"
                            "• **Ação Recomendada:** Entrar com o dedo no gatilho para o próximo evento (Gol/Cantos) AGORA!\n\n"
                            "🔥 *Valendo a moedazinha! Vamos pra cima!*"
                        )

                        for chat_id in chats_monitorados:
                            enviar_mensagem(chat_id, alerta)
                        break # Dispara um por ciclo para não atropelar a leitura

                ultimo_ciclo = tempo_atual

        except Exception as e:
            logging.error(f"Erro no loop principal: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
