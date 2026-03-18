import os
import subprocess
from aiogram import Bot, Dispatcher, types, executor

# ЗАМЕНИ ЭТО на свой новый токен после ревока!
API_TOKEN = '8577086957:AAGSh9ePU6SwSyn3mQC-iIlIT2mqmXCbqew'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Обработчик всех текстовых сообщений (команд)
@dp.message_handler()
async def execute_command(message: types.Message):
    command = message.text
    
    try:
        # Выполняем команду и получаем результат
        process = subprocess.Popen(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        stdout, stderr = process.communicate()
        
        result = stdout if stdout else stderr
        if not result:
            result = "Команда выполнена (без вывода)."
            
        # Лимит сообщения в ТГ — 4096 символов, обрежем на всякий случай
        await message.answer(f"http://googleusercontent.com/immersive_entry_chip/0") 
