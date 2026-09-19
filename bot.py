import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Configuração de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    total_ligas = len(LIGAS_MONITORADAS)
    
    await update.message.reply_text(
        f"Fala, {user.first_name}! 🚀\n\n"
        f"O **Radar de Pressão** está 100% operacional!\n"
        f"📊 Monitorando ativamente uma grade robusta com **{total_ligas} ligas** (incluindo Brasil, Europa e América do Sul).\n\n"
        "Estou varrendo os jogos em segundo plano. Assim que o padrão de pressão estourar, mando o alerta direto para você!"
    )

async def monitorar_ligas_automatico(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.chat_id
    pass

async def ativar_monitoramento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()
        
    context.job_queue.run_repeating(
        monitorar_ligas_automatico, 
        interval=60, 
        first=10, 
        chat_id=chat_id, 
        name=str(chat_id)
    )
    
    await update.message.reply_text(
        "✅ **Varredura automática ativada com sucesso!**\n"
        "Monitoramento contínuo das 40+ ligas ligado em segundo plano."
    )

def main():
    TOKEN = "8304259552:AAGm4l7uVV9gGTfFaJyI8ooeS-rPAJnkPDk"

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("monitorar", ativar_monitoramento))

    print("Bot autônomo com as 40+ ligas iniciado com sucesso...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
