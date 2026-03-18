import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message

# Твой токен и ID (обязательно замени 0 на свой ID!)
TOKEN = "8577086957:AAGSh9ePU6SwSyn3mQC-iIlIT2mqmXCbqew"
ADMIN_ID = 0  # Напиши @userinfobot в телеграм, чтобы узнать свой ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_terminal_command(message: Message):
    # Проверка, что пишет именно хозяин
    if ADMIN_ID != 0 and message.from_user.id != ADMIN_ID:
        return

    command = message.text
    try:
        # Запуск команды в системе Railway
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        result = ""
        if stdout:
            result += f"**Вывод:**\n```\n{stdout.decode('utf-8', errors='ignore')}\n```\n"
        if stderr:
            result += f"**Ошибка:**\n```\n{stderr.decode('utf-8', errors='ignore')}\n```"
        
        await message.answer(result[:4000] if result else "✅ Выполнено", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Ошибка выполнения: {e}")

async def main():
    print("-----------------------------------")
    print("SERVER STARTED: Bot is active")
    print("-----------------------------------")
    
    # Отправка сообщения тебе в личку при старте
    if ADMIN_ID != 0:
        try:
            await bot.send_message(ADMIN_ID, "✅ Бот запущен на Railway и готов принимать команды!")
        except Exception as e:
            print(f"Не удалось отправить сообщение админу: {e}")
            
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
