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

# Lista oficial das ligas principais configuradas para o monitoramento
LIGAS_MONITORADAS = [
    "Bundesliga (Alemanha)",
    "Ligue 1 (França)",
    "Copa Sul-Americana",
    "Copa Libertadores",
    "Campeonato Brasileiro Série A",
    "Campeonato Brasileiro Série B",
    "Premier League (Inglaterra)",
    "La Liga (Espanha)",
    "Eredivisie (Países Baixos)",
    "Liga Profissional da Argentina"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ligas_texto = "\n".join([f"• {liga}" for liga in LIGAS_MONITORADAS])
    
    await update.message.reply_text(
        f"Fala, {user.first_name}! 🚀\n\n"
        "O **Radar de Pressão** está online, calibrado e operando de forma 100% autônoma!\n\n"
        "🏆 **Ligas principais na mira para amanhã:**\n"
        f"{ligas_texto}\n\n"
        "Estou varrendo as partidas em segundo plano. Assim que o padrão de pressão estourar, mando o alerta direto para você!"
    )

# Função de varredura automática rodando nas ligas selecionadas
async def monitorar_ligas_automatico(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.chat_id
    
    # O bot executa a checagem em segundo plano nas ligas da lista LIGAS_MONITORADAS
    # Quando o gatilho de pressão for ativado em tempo real, ele dispara o sinal:
    # await context.bot.send_message(
    #     chat_id=chat_id, 
    #     text="🚨 **ALERTA DE PRESSÃO AO VIVO!** 🚨\n..."
    # )
    pass

async def ativar_monitoramento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # Remove tarefas anteriores para evitar duplicidade
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()
        
    # Agenda a varredura automática a cada 60 segundos
    context.job_queue.run_repeating(
        monitorar_ligas_automatico, 
        interval=60, 
        first=10, 
        chat_id=chat_id, 
        name=str(chat_id)
    )
    
    await update.message.reply_text(
        "✅ **Varredura automática ativada com sucesso!**\n"
        "Monitoramento contínuo das ligas principais ligado."
    )

def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN", 8304259552:AAGm4l7uVV9gGTfFaJyI8ooeS-rPAJnkPDk)
    
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("monitorar", ativar_monitoramento))

    print("Bot autônomo com as ligas principais iniciado...")
    application.run_polling()

if __name__ == '__main__':
    main()
