import asyncio
import logging
import sys
import html
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message

# --- НАСТРОЙКИ ---
TOKEN = "8577086957:AAGSh9ePU6SwSyn3mQC-iIlIT2mqmXCbqew"
ADMIN_ID = 0  # <--- ЗАМЕНИ НА СВОЙ ID (узнай в @userinfobot)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
bot = Bot(token=TOKEN)
dp = Dispatcher()

def split_message(text, max_length=3800):
    """Разрезает текст на части, оборачивая каждую в <pre> для корректного HTML"""
    parts = []
    for i in range(0, len(text), max_length):
        chunk = text[i:i + max_length]
        # Экранируем спецсимволы и оборачиваем в моноширинный блок
        safe_chunk = html.escape(chunk)
        parts.append(f"<pre>{safe_chunk}</pre>")
    return parts

def remove_ansi(text):
    """Удаляет ANSI-последовательности (цвета консоли), которые ломают текст"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

@dp.message(Command("start"))
async def cmd_start(message: Message):
    if ADMIN_ID != 0 and message.from_user.id != ADMIN_ID: return
    await message.answer("<b>🖥 Терминал активен.</b>\nПрисылай команды (например, <code>nmap -F [IP]</code>).", parse_mode="HTML")

@dp.message(F.text)
async def execute_console_command(message: Message):
    if ADMIN_ID != 0 and message.from_user.id != ADMIN_ID: return
    
    command = message.text
    if command.startswith('/'): return

    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            # Увеличим тайм-аут до 5 минут для тяжелых сканов nmap
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300.0)
        except asyncio.TimeoutError:
            process.kill()
            await message.answer("⚠️ <b>Тайм-аут (5 мин).</b> Команда была принудительно остановлена.")
            return

        out = remove_ansi(stdout.decode('utf-8', errors='ignore').strip())
        err = remove_ansi(stderr.decode('utf-8', errors='ignore').strip())

        if out:
            await message.answer("✅ <b>Вывод:</b>", parse_mode="HTML")
            for chunk in split_message(out):
                await message.answer(chunk, parse_mode="HTML")
        
        if err:
            await message.answer("❌ <b>Ошибка/Лог:</b>", parse_mode="HTML")
            for chunk in split_message(err):
                await message.answer(chunk, parse_mode="HTML")
        
        if not out and not err:
            await message.answer("💎 <i>Выполнено без вывода.</i>", parse_mode="HTML")

    except Exception as e:
        await message.answer(f"⚠️ <b>Критическая ошибка:</b>\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def main():
    if ADMIN_ID != 0:
        try:
            await bot.send_message(ADMIN_ID, "🚀 <b>Бот запущен.</b>\nГотов к выполнению команд.", parse_mode="HTML")
        except: pass
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
