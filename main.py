import asyncio
import logging
import sys
import html
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message

# --- ОБЯЗАТЕЛЬНО ЗАПОЛНИ ЭТИ ПОЛЯ ---
TOKEN = "8577086957:AAGSh9ePU6SwSyn3mQC-iIlIT2mqmXCbqew"
ADMIN_ID = 0  # <--- Твой ID (узнай в @userinfobot)

# Настройка логирования для консоли Railway
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    if ADMIN_ID != 0 and message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        "<b>🖥 Терминал активен</b>\n\n"
        "Присылай любую команду (ls, pwd, top) прямым текстом.\n"
        "<i>Будь осторожен с командами удаления!</i>",
        parse_mode="HTML"
    )

# Основной обработчик консольных команд
@dp.message(F.text)
async def execute_console_command(message: Message):
    # Проверка прав доступа
    if ADMIN_ID != 0 and message.from_user.id != ADMIN_ID:
        return

    command = message.text
    
    # Игнорируем другие команды Telegram (начинающиеся с /)
    if command.startswith('/'):
        return

    try:
        # Запуск команды в shell
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Ожидаем завершения (тайм-аут 30 секунд, чтобы бот не завис намертво)
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
        except asyncio.TimeoutError:
            process.kill()
            await message.answer("⚠️ <b>Ошибка:</b> Превышено время ожидания (30 сек).")
            return

        # Декодируем и экранируем спецсимволы для HTML
        def clean_output(data):
            text = data.decode('utf-8', errors='ignore').strip()
            return html.escape(text)

        out_text = clean_output(stdout)
        err_text = clean_output(stderr)

        # Формируем ответ
        response = ""
        if out_text:
            response += f"✅ <b>Вывод:</b>\n<pre>{out_text}</pre>\n"
        if err_text:
            response += f"❌ <b>Ошибка:</b>\n<pre>{err_text}</pre>"
        
        if not response:
            response = "💎 <i>Команда выполнена, вывода нет.</i>"

        # Отправляем ответ частями, если он слишком длинный (лимит ТГ 4096 симв)
        if len(response) > 4000:
            for x in range(0, len(response), 4000):
                await message.answer(response[x:x+4000], parse_mode="HTML")
        else:
            await message.answer(response, parse_mode="HTML")

    except Exception as e:
        await message.answer(f"⚠️ <b>Системный сбой:</b>\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def main():
    logger.info("Бот запускается...")
    
    # Уведомление в Telegram при успешном старте
    if ADMIN_ID != 0:
        try:
            await bot.send_message(ADMIN_ID, "🚀 <b>Система запущена на Railway!</b>\nЖду команд...", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Не удалось отправить пуш админу: {e}")

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен.")
