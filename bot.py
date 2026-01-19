import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
API_KEY = os.environ.get('OPENROUTER_API_KEY')  # Используем ту же переменную
MODEL = os.environ.get('MODEL_NAME', 'deepseek-ai/deepseek-v3.1-terminus')
API_URL = os.environ.get('API_URL', 'https://ai.megallm.io/v1/chat/completions')

SYSTEM_PROMPT = "Ты - Артур (женщина). Отвечаешь в личных сообщениях от первого лица как будто это пишешь ты сама. КРИТИЧЕСКИ ВАЖНО: НИКОГДА не говори что ты бот автоответчик или что отвечаешь за Артура. Ты - это Артур. Стиль: неформальный дружелюбный спокойный. Короткие сообщения 1-2 предложения. Можешь использовать маты но редко и естественно: блять бля нахуй. Иногда пиши капсом для сильных эмоций но не часто. Сокращения: чичас вместо сейчас крч вместо короче. НЕ ставь точку в конце. Минимум запятых. НЕ используй скобки )) вообще. Эмодзи используй РЕДКО и ТОЛЬКО В КОНЦЕ предложения минимум 2 штуки: 😭😭 для очень сильной реакции 🙄🙄 используй ОЧЕНЬ РЕДКО только если реально раздражена 🆘🆘 для шокирующих моментов. Чаще отвечай БЕЗ эмодзи вообще. НИКОГДА не используй черные сердечки и любые сердечки. Запрещённые эмодзи: 😊☺️😃😄🙂🖤❤️💙💚🧡💛💜. Примеры: Я чичас занята. Да щас сделаю. Хз пока не знаю. Окей напишу позже. Была занята. Не помню. Пиши в женском роде: была сделала занята устала. Будь спокойной и естественной не перебарщивай с эмоциями и эмодзи. Большинство ответов должны быть простыми без эмодзи, мат должен быть локанично встроен. Помни: ты НЕ автоответчик ты АРТУР."

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
        print(f"Ошибка get_ai_response: {e}")
        return "Произошла ошибка"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Привет! Я бот для бизнес-аккаунта")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message and update.message.text:
            user_message = update.message.text
            ai_response = get_ai_response(user_message)
            await update.message.reply_text(ai_response)
    except Exception as e:
        print(f"Ошибка handle_message: {e}")

async def handle_all_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        print(f"Получен update: {update}")
        
        # Обработка Business сообщений
        if hasattr(update, 'business_message') and update.business_message:
            biz_msg = update.business_message
            print(f"Business message от {biz_msg.chat.id}: {biz_msg.text}")
            
            if biz_msg.text:
                ai_response = get_ai_response(biz_msg.text)
                
                await context.bot.send_message(
                    chat_id=biz_msg.chat.id,
                    text=ai_response,
                    business_connection_id=biz_msg.business_connection_id
                )
                print(f"Отправлен ответ: {ai_response}")
        
        # Обработка обычных сообщений (для тестирования в личке с ботом)
        elif update.message and update.message.text:
            user_message = update.message.text
            ai_response = get_ai_response(user_message)
            await update.message.reply_text(ai_response)
            
    except Exception as e:
        print(f"Ошибка handle_all_updates: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("Бот запущен в Business режиме!")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL, handle_all_updates))
    
    application.run_polling(allowed_updates=['message', 'business_message', 'business_connection'])

if __name__ == '__main__':
    main()
