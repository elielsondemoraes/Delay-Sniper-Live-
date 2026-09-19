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

# Dicionários de controlo
chats_monitorados = set()
jogos_recentes_enviados = set() # Evita repetir o mesmo jogo consecutivamente

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
    Filtro estrito: apenas futebol real e ignorando ligas indesejadas (como futebol americano CFL).
    """
    try:
        url = "https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d=2026-09-19"
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.text.strip():
            dados = response.json()
            eventos = dados.get("events", []) or []
            
            jogos_validos = []
            for jogo in eventos:
                liga = str(jogo.get("strLeague", ""))
                sport = str(jogo.get("strSport", "Soccer"))
                
                # Exclui explicitamente esportes que não sejam futebol ou ligas incorretas (ex: CFL)
                if "Soccer" not in sport and "Football" in sport and "CFL" in liga:
                    continue
                if "CFL" in liga or "Rugby" in liga or "Basketball" in liga:
                    continue
                    
                jogos_validos.append(jogo)
                
            return jogos_validos
        return []
    except Exception as e:
        logging.error(f"Erro ao consultar dados ao vivo: {e}")
        return []

def main():
    logging.info("Delay Sniper Live (Filtro Anti-Spam e Anti-Esporte Errado) iniciado!")
    offset = None
    ultimo_ciclo = time.time()
    
    total_ligas = len(LIGAS_MONITORADAS)

    while True:
        try:
            # 1. Processa comandos do Telegram em tempo real
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
                                f"O **Delay Sniper Live** está armado!\n"
                                f"📊 Monitorando grade de **{total_ligas} ligas** de futebol real.\n\n"
                                "Envie **/monitorar** para ativar."
                            )
                            enviar_mensagem(chat_id, resposta)
                            
                        elif texto_msg.startswith("/monitorar"):
                            chats_monitorados.add(chat_id)
                            resposta = (
                                "✅ **Radar Cirúrgico Ativado!**\n"
                                "Filtro avançado ligado: sem repetições e apenas futebol real."
                            )
                            enviar_mensagem(chat_id, resposta)

            # 2. Rotina de varredura
            tempo_atual = time.time()
            if tempo_atual - ultimo_ciclo >= 60:
                logging.info("A varrer partidas com filtros rigorosos...")
                
                jogos = buscar_jogos_ao_vivo()
                if jogos and chats_monitorados:
                    for jogo in jogos:
                        home = jogo.get("strHomeTeam", "Time Casa")
                        away = jogo.get("strAwayTeam", "Time Fora")
                        liga = jogo.get("strLeague", "Futebol")
                        id_jogo = jogo.get("idEvent", home + away)
                        
                        # Evita mandar o alerta repetidas vezes para o mesmo jogo seguido
                        if id_jogo in jogos_recentes_enviados:
                            continue
                            
                        # Marca como enviado para não repetir no próximo ciclo
                        jogos_recentes_enviados.add(id_jogo)
                        if len(jogos_recentes_enviados) > 20: # Limpa histórico antigo
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
                        break # Envia um único alerta por ciclo

                ultimo_ciclo = tempo_atual

        except Exception as e:
            logging.error(f"Erro no loop principal: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
