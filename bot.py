import os
import telebot
import requests

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
MODEL = os.environ.get('MODEL_NAME', 'meta-llama/llama-3.1-8b-instruct:free')

bot = telebot.TeleBot(BOT_TOKEN)

# Настройте характер бота здесь:
SYSTEM_PROMPT = """Ты - дружелюбный помощник, который отвечает за пользователя в личных сообщениях. 
Отвечай естественно, живо и по-человечески. 
Будь кратким, но информативным."""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот с AI. Напиши мне что-нибудь!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
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
                    {"role": "user", "content": message.text}
                ]
            },
            timeout=30
        )
        
        response_data = response.json()
        
        # Проверяем разные варианты ответа
        if 'choices' in response_data and len(response_data['choices']) > 0:
            ai_response = response_data['choices'][0]['message']['content']
        elif 'error' in response_data:
            ai_response = f"Ошибка API: {response_data['error'].get('message', 'Неизвестная ошибка')}"
        else:
            ai_response = f"Неожиданный формат ответа: {response_data}"
        
        bot.reply_to(message, ai_response)
        
    except requests.exceptions.Timeout:
        bot.reply_to(message, "Превышено время ожидания ответа. Попробуйте ещё раз.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")
        print(f"Полная ошибка: {e}")

if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()
