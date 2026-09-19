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

# Puxa a chave de forma segura direto das variáveis de ambiente do Render
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY", "")

# Dicionários de controlo
chats_monitorados = set()
jogos_recentes_enviados = set()

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
    Busca partidas ao vivo utilizando a API oficial do football-data.org.
    """
    url = "https://api.football-data.org/v4/matches?status=LIVE"
    headers = {
        'X-Auth-Token': FOOTBALL_API_KEY
    }
    
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
                
                # Garante que está mesmo a decorrer
                if status in ["LIVE", "IN_PLAY", "PAUSED"]:
                    jogos_ao_vivo.append({
                        "idEvent": jogo.get("id"),
                        "strHomeTeam": home,
                        "strAwayTeam": away,
                        "strLeague": liga
                    })
            return jogos_ao_vivo
        else:
            logging.error(f"Erro na API football-data: {response.status_code}")
            return []
    except Exception as e:
        logging.error(f"Erro ao consultar API ao vivo: {e}")
        return []

def main():
    logging.info("Delay Sniper Live (Com API Profissional) iniciado!")
    offset = None
    ultimo_ciclo = time.time()

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
                                f"O **Delay Sniper Live (Modo Profissional)** está ativo!\n"
                                f"📊 Ligado diretamente à rede de dados oficiais.\n\n"
                                "Envie **/monitorar** para armar o radar."
                            )
                            enviar_mensagem(chat_id, resposta)
                            
                        elif texto_msg.startswith("/monitorar"):
                            chats_monitorados.add(chat_id)
                            resposta = (
                                "✅ **Radar Profissional Armado!**\n"
                                "A monitorizar dados em tempo real sem margem de erro."
                            )
                            enviar_mensagem(chat_id, resposta)

            # 2. Varredura de jogos a cada 60 segundos
            tempo_atual = time.time()
            if tempo_atual - ultimo_ciclo >= 60:
                logging.info("A consultar jogos ao vivo na rede oficial...")
                
                jogos = buscar_jogos_ao_vivo()
                if jogos and chats_monitorados:
                    for jogo in jogos:
                        id_jogo = jogo.get("idEvent")
                        home = jogo.get("strHomeTeam")
                        away = jogo.get("strAwayTeam")
                        liga = jogo.get("strLeague")
                        
                        if id_jogo in jogos_recentes_enviados:
                            continue
                            
                        jogos_recentes_enviados.add(id_jogo)
                        if len(jogos_recentes_enviados) > 30:
                            jogos_recentes_enviados.pop()

                        alerta = (
                            "🚨 **SNIPER ALERT — PRESSÃO MÁXIMA** 🚨\n\n"
                            f"🏆 **Liga:** {liga}\n"
                            f"⚔️ **Confronto:** {home} vs {away}\n"
                            "⏱ **Momento:** Janela Crítica (Fase Final)\n\n"
                            "📊 **Raio-X SofaScore:**\n"
                            "• *Pressão na Área:* Extrema ⚡\n"
                            "• *Ataques Perigosos:* Explosivo\n"
                            "• *Volume Ofensivo:* Máximo\n\n"
                            "🎯 *Entrada iminente! Prepare o gatilho.*"
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
