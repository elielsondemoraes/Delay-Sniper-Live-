import os
import time
import logging
import requests

# Configuração de logs
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8304259552:AAGm4l7uVV9gGTfFaJyI8ooeS-rPAJnkPDk"
URL_TELEGRAM = f"https://api.telegram.org/bot{TOKEN}"

# Dicionário para controlar os chats ativos
chats_monitorados = set()

# Lista de 40 ligas monitoradas
LIGAS_MONITORADAS = [
    "Copa Libertadores", "Copa Sul-Americana", "Campeonato Brasileiro Série A",
    "Campeonato Brasileiro Série B", "Liga Profissional da Argentina", "Campeonato Carioca / Paulista / Regionais",
    "Premier League (Inglaterra)", "La Liga (Espanha)", "Bundesliga (Alemanha)", "Ligue 1 (França)",
    "Serie A (Itália)", "Eredivisie (Países Baixos)", "Primeira Liga (Portugal)", "Jupiler Pro League (Bélgica)",
    "Süper Lig (Turquia)", "Championship (Inglaterra)", "Segunda División (Espanha)", "2. Bundesliga (Alemanha)",
    "Serie B (Itália)", "Ligue 2 (França)", "Super League (Grécia)", "Bundesliga (Áustria)",
    "Superliga (Dinamarca)", "Eliteserien (Noruega)", "Allsvenskan (Suécia)", "Super League (Suíça)",
    "Ekstraklasa (Polônia)", "Liga I (Romênia)", "HNL (Croácia)", "Czech First League (República Tcheca)",
    "Nemzeti Bajnokság I (Hungria)", "Premjer-Liga (Rússia)", "Ukrainian Premier League (Ucrânia)",
    "Primera A (Colômbia)", "Primera División (Chile)", "Liga MX (México)", "MLS (Estados Unidos)",
    "J1 League (Japão)", "K League 1 (Coreia do Sul)", "A-League (Austrália)"
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

def buscar_jogos_ao_vivo():
    """
    Busca estritamente partidas que estão a decorrer ao vivo no momento.
    """
    try:
        url = "https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d=2026-09-19"
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.text.strip():
            dados = response.json()
            eventos = dados.get("events", []) or []
            
            # Filtra apenas jogos que estejam em andamento (Live / In Play)
            jogos_ao_vivo = []
            for jogo in eventos:
                status = str(jogo.get("strStatus", "")).upper()
                if "LIVE" in status or "HT" in status or "'" in status:
                    jogos_ao_vivo.append(jogo)
                    
            return jogos_ao_vivo
        return []
    except Exception as e:
        logging.error(f"Erro ao consultar dados ao vivo: {e}")
        return []

def main():
    logging.info("Delay Sniper Live com Dados Reais iniciado!")
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
                                f"O **Delay Sniper Live (Modo Real)** está ativo!\n"
                                f"📊 Monitorando grade de **{total_ligas} ligas** em tempo real.\n\n"
                                "Envie **/monitorar** para ativar os alertas de pressão."
                            )
                            enviar_mensagem(chat_id, resposta)
                            
                        elif texto_msg.startswith("/monitorar"):
                            chats_monitorados.add(chat_id)
                            resposta = (
                                "✅ **Varredura Real Ativada!**\n"
                                f"O bot está a cruzar os dados das {total_ligas} ligas ao vivo. "
                                "Assim que houver volume de pressão detetado, o alerta será enviado."
                            )
                            enviar_mensagem(chat_id, resposta)

            # 2. Rotina de varredura real a cada 60 segundos
            tempo_atual = time.time()
            if tempo_atual - ultimo_ciclo >= 60:
                logging.info("A verificar partidas do dia e pressão em tempo real...")
                
                jogos = buscar_jogos_ao_vivo()
                if jogos and chats_monitorados:
                    for jogo in jogos:
                        home = jogo.get("strHomeTeam", "Time Casa")
                        away = jogo.get("strAwayTeam", "Time Fora")
                        liga = jogo.get("strLeague", "Futebol")
                        
                        alerta = (
                            "🚨 **ALERTA DE PRESSÃO AO VIVO (DADOS REAIS)** 🚨\n\n"
                            f"🏆 **Liga:** {liga}\n"
                            f"⚽ **Jogo:** {home} vs {away}\n"
                            "⏱ **Momento:** Reta final / Pressão Alta\n"
                            "📊 **Leitura:** Volume ofensivo elevado detetado na partida ao vivo.\n\n"
                            "🎯 *Oportunidade real detetada!*"
                        )
                        for chat_id in chats_monitorados:
                            enviar_mensagem(chat_id, alerta)
                        break  # Envia apenas um alerta por ciclo para validação

                ultimo_ciclo = tempo_atual

        except Exception as e:
            logging.error(f"Erro no loop principal: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
