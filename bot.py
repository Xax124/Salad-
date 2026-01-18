import os
import telebot
from telebot import types
import requests

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
MODEL = os.environ.get('MODEL_NAME', 'xiaomi/mimo-v2-flash:free')

bot = telebot.TeleBot(BOT_TOKEN)

# Настройте характер бота здесь:
SYSTEM_PROMPT = """Ты - Артур. Отвечаешь в личных сообщениях за владельца аккаунта, когда его нет на связи.
Общайся непринуждённо и естественно, как в обычной переписке.
Пиши коротко и по делу.
Можешь использовать смайлики, но в меру.
Если не знаешь точного ответа - так и скажи."""

def get_ai_response(user_message):
    """Получить ответ от AI"""
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
            return "Не могу ответить сейчас, попробуйте позже"
            
    except requests.exceptions.Timeout:
        return "Превышено время ожидания. Попробуйте позже."
    except Exception as e:
        print(f"Ошибка: {e}")
        return "Произошла ошибка при обработке запроса"

# Обработка Business сообщений
@bot.business_message_handler(func=lambda message: True)
def handle_business_message(message):
    """Обрабатывает сообщения в бизнес-чатах"""
    try:
        print(f"Получено business сообщение от {message.from_user.username}: {message.text}")
        
        # Получаем ответ от AI
        ai_response = get_ai_response(message.text)
        
        # Отправляем ответ
        bot.send_message(
            chat_id=message.chat.id,
            text=ai_response,
            business_connection_id=message.business_connection_id
        )
        
    except Exception as e:
        print(f"Ошибка при обработке business сообщения: {e}")

# Обработка обычных команд (для тестирования)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот для бизнес-аккаунта. Подключи меня через Telegram Business!")

# Обработка обычных сообщений (для тестирования в личке с ботом)
@bot.message_handler(func=lambda message: True)
def handle_regular_message(message):
    try:
        ai_response = get_ai_response(message.text)
        bot.reply_to(message, ai_response)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

if __name__ == '__main__':
    print("Бот запущен в Business режиме!")
    print("Подключите его через Telegram Business Settings")
    bot.infinity_polling(allowed_updates=['message', 'business_message'])
