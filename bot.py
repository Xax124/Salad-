import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
MODEL = os.environ.get('MODEL_NAME', 'xiaomi/mimo-v2-flash:free')

SYSTEM_PROMPT = "Ты - Артур (женщина). Отвечаешь в личных сообщениях от первого лица как будто это пишешь ты сама. КРИТИЧЕСКИ ВАЖНО: НИКОГДА не говори что ты бот автоответчик или что отвечаешь за Артура. Ты - это Артур. Стиль: неформальный дружелюбный с шутками. Короткие сообщения 1-2 предложения. Используй маты: блять бля нахуй. Пиши капсом для эмоций: БЛЯТЬ ЧЕ ТЫ АХАХАХАХА. Сокращения: чичас вместо сейчас крч вместо короче. НЕ ставь точку в конце. Минимум запятых. Используй ТОЛЬКО чётное количество скобок )) или )))). Используй ТОЛЬКО чётное количество эмодзи. Эмодзи только эти по 2-4 штуки: 😭😭 для драматизма 🙄🙄 для сарказма 🆘🆘 для шокирующих моментов. Запрещённые эмодзи: 😊☺️😃😄🙂. Примеры: Норм чичас занята немного. Да блять щас сделаю)). АХАХАХА ЧТО 😭😭🆘🆘. Крч не знаю пока. Окей напишу позже. Пиши в женском роде: была сделала занята устала. Если не знаешь ответ: Хз пока Не помню блять Надо подумать. Помни: ты НЕ автоответчик ты АРТУР."

def get_ai_response(user_message):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ]
            },
            timeout=30
        )
        
        response_data = response.json()
        
        if 'choices' in response_data and len(response_data['choices']) > 0:
            return response_data['choices'][0]['message']['content']
        elif 'error' in response_data:
            return f"Ошибка API: {response_data['error'].get('message', 'Неизвестная ошибка')}"
        else:
            return "Не могу ответить сейчас"
            
    except Exception as e:
        print(f"Ошибка: {e}")
        return "Произошла ошибка"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для бизнес-аккаунта")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text
        ai_response = get_ai_response(user_message)
        await update.message.reply_text(ai_response)
    except Exception as e:
        print(f"Ошибка: {e}")
        await update.message.reply_text("Произошла ошибка")

async def handle_business_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.business_message:
            user_message = update.business_message.text
            ai_response = get_ai_response(user_message)
            
            await context.bot.send_message(
                chat_id=update.business_message.chat.id,
                text=ai_response,
                business_connection_id=update.business_message.business_connection_id
            )
    except Exception as e:
        print(f"Ошибка business: {e}")

def main():
    print("Бот запущен в Business режиме!")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.ALL, handle_business_message))
    
    application.run_polling(allowed_updates=['message', 'business_message', 'business_connection'])

if __name__ == '__main__':
    main()
