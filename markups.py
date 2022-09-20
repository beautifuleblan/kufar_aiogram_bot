from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

btnStart = KeyboardButton('🟢️Запуск')
btnStop = KeyboardButton('🚫Остановка')
btnMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnStart, btnStop)
