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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Fala, {user.first_name}! 🚀\n\n"
        "O **Radar de Pressão** está online e operando nas 40+ ligas!\n"
        "Estou monitorando o início dos jogos em segundo plano. Assim que rolar um cenário de abafa ou pressão forte, mandarei o alerta direto aqui para você."
    )

# Função de varredura automática que roda em segundo plano
async def monitorar_ligas_automatico(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.chat_id
    
    # ----------------------------------------------------
    # AQUI ENTRARIA A SUA LÓGICA DE BUSCA AUTOMÁTICA NAS LIGAS
    # (Ex: consulta a API de futebol, varredura de estatísticas, etc.)
    # ----------------------------------------------------
    
    # Exemplo simulado de alerta automático gerado pelo bot:
    # Quando o script detectar pressão real em um jogo ao vivo, ele dispara:
    # await context.bot.send_message(
    #     chat_id=chat_id, 
    #     text="🚨 **ALERTA DE PRESSÃO AO VIVO!** 🚨\nPartida: Time A x Time B\nCenário: Pressão forte e abafamento na área. Fique de olho no gol!"
    # )
    pass

async def ativar_monitoramento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # Remove jobs anteriores para evitar duplicação
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()
        
    # Agenda a varredura automática para rodar a cada 60 segundos
    context.job_queue.run_repeating(
        monitorar_ligas_automatico, 
        interval=60, 
        first=10, 
        chat_id=chat_id, 
        name=str(chat_id)
    )
    
    await update.message.reply_text(
        "✅ **Varredura automática ativada!**\n"
        "Estou rastreando as 40+ ligas continuamente. Avisarei assim que achar oportunidades."
    )

def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN", "8304259552:AAGm4l7uVV9gGTfFaJyI8ooeS-rPAJnkPDk")
    
    application = ApplicationBuilder().token(TOKEN).build()

    # Adiciona comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("monitorar", ativar_monitoramento))

    print("Bot autônomo de radar iniciado com sucesso...")
    application.run_polling()

if __name__ == '__main__':
    main()
