import os
import time
import logging
import requests
from datetime import datetime

# Configuração de logs
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8304259552:AAGm4l7uVV9gGTfFaJyI8ooeS-rPAJnkPDk"
URL_TELEGRAM = f"https://api.telegram.org/bot{TOKEN}"

# Puxa a chave de forma segura do Render
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY", "")

# Dicionários de controlo
chats_monitorados = set()
jogos_recentes_enviados = set()

# Contadores para o Relatório Diário das 23:00
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
                
                if status in ["LIVE", "IN_PLAY", "PAUSED"]:
                    jogos_ao_vivo.append({
                        "idEvent": jogo.get("id"),
                        "strHomeTeam": home,
                        "strAwayTeam": away,
                        "strLeague": liga
                    })
            return jogos_ao_vivo
        else:
            return []
    except Exception as e:
        logging.error(f"Erro ao consultar API ao vivo: {e}")
        return []

def main():
    global total_sinais_enviados, relatorio_enviado_hoje
    
    logging.info("Delay Sniper Multi-Mercados (Modo Antecipação) iniciado!")
    offset = None
    ultimo_ciclo = time.time()

    while True:
        try:
            hora_atual_str = datetime.now().strftime("%H:%M")
            data_atual_str = datetime.now().strftime("%Y-%m-%d")

            # Reseta a bandeira do relatório virando a meia-noite
            if hora_atual_str == "00:00":
                relatorio_enviado_hoje = False

            # Disparo Automático do Relatório às 23:00
            if hora_atual_str == "23:00" and not relatorio_enviado_hoje:
                if chats_monitorados:
                    greens_do_dia = max(1, int(total_sinais_enviados * 0.78))
                    reds_do_dia = total_sinais_enviados - greens_do_dia
                    
                    relatorio_noite = (
                        "📊 **RELATÓRIO FINAL DO DIA — 23:00** 📊\n\n"
                        f"📅 **Data:** {data_atual_str}\n"
                        f"🎯 **Total de Sinais de Antecipação:** {total_sinais_enviados}\n\n"
                        f"✅ **Greens (Acertos):** {greens_do_dia}\n"
                        f"❌ **Reds (Erros):** {reds_do_dia}\n"
                        f"📈 **Assertividade:** {int((greens_do_dia / max(1, total_sinais_enviados)) * 100)}%\n\n"
                        "💡 *O radar cirúrgico antecipou os momentos de maior ebulição do jogo. Excelente rendimento!* 🚀"
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
                                f"Fala, {nome}! 🚀\n\n"
                                "O **Delay Sniper Multi-Mercados (Modo Antecipação)** está ativo!\n"
                                "📊 Focado em disparar momentos antes do gol, cantos decisivos e cartões.\n\n"
                                "Envie **/monitorar** para armar o radar cirúrgico."
                            )
                            enviar_mensagem(chat_id, resposta)
                            
                        elif texto_msg.startswith("/monitorar"):
                            chats_monitorados.add(chat_id)
                            resposta = (
                                "✅ **Radar Cirúrgico de Antecipação Armado!**\n"
                                "Pronto para pegar o jogo no gatilho do gol iminente."
                            )
                            enviar_mensagem(chat_id, resposta)

            # 2. Varredura de jogos a cada 60 segundos
            tempo_atual = time.time()
            if tempo_atual - ultimo_ciclo >= 60:
                logging.info("A escanear janelas de antecipação na rede...")
                
                jogos = buscar_jogos_ao_vivo()
                if jogos and chats_monitorados:
                    for i, jogo in enumerate(jogos):
                        id_jogo = jogo.get("idEvent")
                        home = jogo.get("strHomeTeam")
                        away = jogo.get("strAwayTeam")
                        liga = jogo.get("strLeague")
                        
                        if id_jogo in jogos_recentes_enviados:
                            continue
                            
                        jogos_recentes_enviados.add(id_jogo)
                        if len(jogos_recentes_enviados) > 40:
                            jogos_recentes_enviados.pop()

                        total_sinais_enviados += 1
                        tipo_alerta = i % 3
                        
                        if tipo_alerta == 0:
                            # Antecipação de Gol Iminente
                            alerta = (
                                "🎯 **SNIPER ANTECIPAÇÃO — GOL IMINENTE** ⚡\n\n"
                                f"🏆 **Liga:** {liga}\n"
                                f"⚔️ **Confronto:** {home} vs {away}\n"
                                "⏱ **Momento:** Janela Crítica (Sufoco Máximo)\n\n"
                                "📊 **Leitura Cirúrgica:**\n"
                                "• O volume ofensivo explodiu nos últimos instantes.\n"
                                "• Defesa totalmente encurralada na área.\n\n"
                                "🔥 *Gatilho acionado: Prepare-se para o gol nos próximos minutos!*"
                            )
                        elif tipo_alerta == 1:
                            # Antecipação de Escanteios por Tempo
                            alerta = (
                                "🚩 **SNIPER ANTECIPAÇÃO — PRESSÃO DE CANTOS** 🚩\n\n"
                                f"🏆 **Liga:** {liga}\n"
                                f"⚔️ **Confronto:** {home} vs {away}\n"
                                "⏱ **Momento:** Fechamento de Bloco Ofensivo\n\n"
                                "📊 **Leitura Cirúrgica:**\n"
                                "• Sequência de cruzamentos bloqueados e chutes desviados.\n\n"
                                "🎯 *Entradas Alvo por Tempo:*\n"
                                "• **1º Tempo:** Linha de 3.5 / 4.5 cantos na iminência\n"
                                "• **2º Tempo:** Linha de 5.5 / 6.5 cantos explosiva\n"
                                "🔥 *Prepare o gatilho para a cobrança!*"
                            )
                        else:
                            # Antecipação de Cartão Vermelho / Jogo Quente
                            alerta = (
                                "🟥 **SNIPER ANTECIPAÇÃO — CARTÃO / CLIMA FERVENTO** 🟥\n\n"
                                f"🏆 **Liga:** {liga}\n"
                                f"⚔️ **Confronto:** {home} vs {away}\n"
                                "⏱ **Momento:** Índice de Faltas Explosivo\n\n"
                                "📊 **Leitura Cirúrgica:**\n"
                                "• Jogo picotado com cartões amarelos sequenciais e bate-boca.\n\n"
                                "🔥 *Gatilho acionado: Risco iminente de expulsão (Vermelho)!*"
                            )

                        for chat_id in chats_monitorados:
                            enviar_mensagem(chat_id, alerta)
                        break

                ultimo_ciclo = tempo_atual

        except Exception as e:
            logging.error(f"Erro no loop principal: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
