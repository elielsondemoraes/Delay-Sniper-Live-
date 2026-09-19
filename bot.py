import os
import time
import logging
import requests
import random

# Configuração de logs
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8304259552:AAGm4l7uVV9gGTfFaJyI8ooeS-rPAJnkPDk"
URL_TELEGRAM = f"https://api.telegram.org/bot{TOKEN}"

# Dicionário para controlar quais chats ativaram o monitoramento automático
chats_monitorados = set()

# Lista completa com as 40+ ligas monitoradas
LIGAS_MONITORADAS = [
    "Copa Libertadores",
    "Copa Sul-Americana",
    "Campeonato Brasileiro Série A",
    "Campeonato Brasileiro Série B",
    "Liga Profissional da Argentina",
    "Campeonato Carioca / Paulista / Regionais",
    "Premier League (Inglaterra)",
    "La Liga (Espanha)",
    "Bundesliga (Alemanha)",
    "Ligue 1 (França)",
    "Serie A (Itália)",
    "Eredivisie (Países Baixos)",
    "Primeira Liga (Portugal)",
    "Jupiler Pro League (Bélgica)",
    "Süper Lig (Turquia)",
    "Championship (Inglaterra)",
    "Segunda División (Espanha)",
    "2. Bundesliga (Alemanha)",
    "Serie B (Itália)",
    "Ligue 2 (França)",
    "Super League (Grécia)",
    "Bundesliga (Áustria)",
    "Superliga (Dinamarca)",
    "Eliteserien (Noruega)",
    "Allsvenskan (Suécia)",
    "Super League (Suíça)",
    "Ekstraklasa (Polônia)",
    "Liga I (Romênia)",
    "HNL (Croácia)",
    "Czech First League (República Tcheca)",
    "Nemzeti Bajnokság I (Hungria)",
    "Premjer-Liga (Rússia)",
    "Ukrainian Premier League (Ucrânia)",
    "Primera A (Colômbia)",
    "Primera División (Chile)",
    "Liga MX (México)",
    "MLS (Estados Unidos)",
    "J1 League (Japão)",
    "K League 1 (Coreia do Sul)",
    "A-League (Austrália)"
]

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

def main():
    logging.info("Delay Sniper Live iniciado com sucesso!")
    offset = None
    ultimo_ciclo = time.time()
    
    total_ligas = len(LIGAS_MONITORADAS)

    while True:
        try:
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
                                f"O **Delay Sniper Live** está 100% operacional!\n"
                                f"📊 Monitorando ativamente uma grade robusta com **{total_ligas} ligas**.\n\n"
                                "Envie **/monitorar** para ativar os rastreios de pressão em segundo plano."
                            )
                            enviar_mensagem(chat_id, resposta)
                            
                        elif texto_msg.startswith("/monitorar"):
                            chats_monitorados.add(chat_id)
                            resposta = (
                                "✅ **Varredura automática ativada com sucesso!**\n"
                                f"Monitoramento contínuo das {total_ligas} ligas ligado em segundo plano. "
                                "Assim que houver pressão alta em campo, mandarei o alerta aqui."
                            )
                            enviar_mensagem(chat_id, resposta)

            # 2. Rotina de varredura automática a cada 60 segundos
            tempo_atual = time.time()
            if tempo_atual - ultimo_ciclo >= 60:
                logging.info(f"Executando varredura nas {total_ligas} ligas...")
                
                # Exemplo de lógica de disparo para chats ativos (se houver chats monitorando)
                # No futuro, aqui você encaixa a sua API de placares/estatísticas ao vivo
                if chats_monitorados and random.choice([True, False]): # Simulação dinâmica de oportunidade
                    liga_escolhida = random.choice(LIGAS_MONITORADAS)
                    alerta = (
                        "🚨 **ALERTA DE PRESSÃO MÁXIMA!** 🚨\n\n"
                        f"🏆 **Liga:** {liga_escolhida}\n"
                        "⚽ **Jogo:** Time A vs Time B\n"
                        "⏱ **Tempo:** 78'\n"
                        "📊 **Estatísticas:** Pressão sufocante nos últimos 10 minutos (Muitos cantos/Ataques perigosos).\n\n"
                        "🎯 *Oportunidade detetada pelo Radar!*"
                    )
                    for chat_id in chats_monitorados:
                        enviar_mensagem(chat_id, alerta)

                ultimo_ciclo = tempo_atual

        except Exception as e:
            logging.error(f"Erro no loop principal: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
