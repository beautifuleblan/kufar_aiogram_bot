#!/usr/bin/env python
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.utils import markdown
from markups import *
from parser import parse_data
from loguru import logger
from config import API_TOKEN


storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
# loop = asyncio.get_event_loop()
dp = Dispatcher(bot, storage=storage)
tasks = {}


async def on_startup(_):
    print('Бот успешно запущен! Для управления перейдите в Telegram.\n'
          'Во избежание неполадок не рекомендуется во время работы бота пользоваться сайтом https://www.kufar.by/')


async def send_welcome(message: types.Message):
    await message.answer(f"Привет, {message.from_user['first_name']}!\n"
                         f"Это бот-парсер сайта Kufar.by\n"
                         f"Для начала работы воспользуйтесь кнопкой 🟢Запуск.", reply_markup=btnMenu)

class FSMAdmin(StatesGroup):
    url = State()


async def fsm_start(message: types.Message):
    worker: asyncio.Task = tasks.get(message.from_user.id)
    if not worker:
        await FSMAdmin.url.set()
        await message.answer('Введите ссылку, которая начинается с https://www.kufar.by/',
                             disable_web_page_preview=True)
    if worker:
        if worker.cancelled():
            await FSMAdmin.url.set()
            await message.answer('Введите ссылку, которая начинается с https://www.kufar.by/',
                                 disable_web_page_preview=True)
        else:
            await message.answer('⛔️Ошибка! Бот уже запущен.')


async def load_url(message: types.Message, state: FSMContext):
    global tasks
    async with state.proxy() as data:
        data['url'] = message.text.strip()
        task = asyncio.create_task(output_data(message, data['url']))
        tasks[message.from_user.id] = task
        await message.answer('Бот успешно запущен!')
    await state.finish()


async def output_data(message: types.Message, url: str):
    await asyncio.sleep(15)
    links_to_ignore = []
    while True:
        try:
            name, price, link = await parse_data(url)
            if link not in links_to_ignore:
                links_to_ignore.append(link)
                await message.answer('❗️Новое объявление!\n'
                                     f'💭Заголовок: {name}\n'
                                     f'💭Цена: {price}\n'
                                     f'💭{markdown.hlink("Ссылка на объявление", link)}',
                                     parse_mode='HTML', disable_web_page_preview=True)
            await asyncio.sleep(10)
        except Exception as ex:
            logger.error(ex)


async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK')


async def stop_parser(message: types.Message):
    global tasks
    worker: asyncio.Task = tasks.get(message.from_user.id)
    if worker:
        if worker.cancelled():
            await message.answer('⛔️Ошибка! Бот уже остановлен.')
        else:
            worker.cancel()
            await message.answer('Бот успешно остановлен!')
    else:
        await message.answer('⛔️Ошибка! Бот уже остановлен.')


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_message_handler(fsm_start, Text(equals='🟢️Запуск'))
    dp.register_message_handler(load_url, Text(contains='kufar.by'), state=FSMAdmin.url)
    dp.register_message_handler(cancel_handler, Text(equals='🚫Остановка'), state=FSMAdmin.url)
    dp.register_message_handler(stop_parser, Text(equals='🚫Остановка'))


if __name__ == '__main__':
    register_handlers(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)