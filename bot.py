import asyncio
import logging
import time
import threading

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile, \
    URLInputFile, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State

from cod import get_map_cell
from cod2 import get_info_by_ip

class States(StatesGroup):
    difficulty = State()
    game = State()

logging.basicConfig(level=logging.INFO)
bot = Bot(token="5993524543:AAGWT0Ql05FPZL8Xtuduee4bwNN4S7NcCw0")
dp = Dispatcher()
difficulty = ["easy", "medium", "hard"]
difficulty1 = {
    "easy": [5, 5],
    "medium": [7, 7],
    "hard": [10, 10],

}
maps = {}

def keyboard():
    # создаем кнопки
    buttons = [
        [
            types.InlineKeyboardButton(text='easy', callback_data='game_easy', ),
            types.InlineKeyboardButton(text='medium', callback_data='game_medium',),
            types.InlineKeyboardButton(text='hard', callback_data='game_hard', )
        ],

    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_keyboard():
    # создаем кнопки
    buttons = [
        [
            types.InlineKeyboardButton(text='↑', callback_data='up', ),
        ],
        [
            types.InlineKeyboardButton(text='←', callback_data='left', ),
            types.InlineKeyboardButton(text='→', callback_data='right'),
        ],
        [
            types.InlineKeyboardButton(text='↓', callback_data='down', ),
        ],
        [
            types.InlineKeyboardButton(text='Change the difficulty ', callback_data='1', ),
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_map_str(map_cell, player, rows, cols):
    a = 0
    # создаем строку для карты.
    map_str = ""
    # проходим по всей вертикали
    for y in range(rows * 2 - 1):
        # проходим по всей горизонтали
        for x in range(cols * 2 - 1):
            # если текущая ячейка в map_cell является True, тогда.
            if map_cell[x + y * (cols * 2 - 1)]:
                a += 1
                # добавляем символ.
                map_str += "⬛"
                # если координаты совпадают с координатами игрока, тогда.
            elif (x, y) == player:
                a += 1
                # мы должны добавить символ.
                map_str += "🔴"
                # или (во всех остальных случаях.)
            else:
                # Проверка на последнюю итерацию
                if x == cols * 2 - 2 and y == rows * 2 - 2:
                    map_str += "☠️"
                    break
                a += 1
                # добавляем символ.
                map_str += "⬜"
                # добавляем перенос строки в map_cell, после прохождения по всей горизонтали.
        map_str += "\n"

    # возвращаем то, что получилось, в карту.
    return map_str

@dp.message(Command("play"))
async def cmd_start(message: types.Message):
    await message.answer("Choose the difficulty", reply_markup=keyboard())

@dp.callback_query(F.data == "1")
async def cmd_start(query: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text("❤️Choose the difficulty❤️", query.message.chat.id,
                                query.message.message_id, reply_markup=keyboard())

@dp.callback_query(F.data.startswith("game"))
async def cmd_start(query: types.CallbackQuery, state: FSMContext):
    a = difficulty1[query.data.split("_")[1]]
    await state.update_data(difficulty=a)
    # cоздаем лаберинт
    map_cell = get_map_cell(a[0], a[1])

    # содержет информацыю о лаберинте и где он находится
    user_data = {
        'map': map_cell,
        'x': 0,
        'y': 0
    }

    maps[query.message.chat.id] = user_data
    await bot.edit_message_text(get_map_str(map_cell, (0, 0), a[0], a[1]),
                                query.message.chat.id,
                                query.message.message_id,
                                reply_markup=get_keyboard())

    current_time = int(time.time())
    global neu_time
    if a[0] == 5:
        neu_time = current_time + 100
    elif a[0] == 7:
        neu_time = current_time + 10000
    elif a[0] == 10:
        neu_time = current_time + 10000


@dp.callback_query()
async def callback_func(query: types.CallbackQuery, bot: Bot, state: FSMContext):
    b = await state.get_data()
    fild = b["difficulty"]
    rows, cols = fild[0], fild[1]
    user_data = maps[query.message.chat.id]
    new_x, new_y = user_data['x'], user_data['y']


    if query.data == 'left':
        new_x -= 1
    if query.data == 'right':
        new_x += 1
    if query.data == 'up':
        new_y -= 1
    if query.data == 'down':
        new_y += 1

    if new_x < 0 or new_x > 2 * cols - 2 or new_y < 0 or new_y > rows * 2 - 2:
        return None
    if user_data['map'][new_x + new_y * (cols * 2 - 1)]:
        return None

    user_data['x'], user_data['y'] = new_x, new_y
    maps[query.message.chat.id] = user_data

    if neu_time <= int(time.time()):
        await bot.edit_message_text(f"You lose", query.message.chat.id,
                                    query.message.message_id)
        return None

    if new_x == cols * 2 - 2 and new_y == rows * 2 - 2:

        if rows == 5:
            await bot.edit_message_text("You win nab", query.message.chat.id,
                                        query.message.message_id)
        elif rows == 7:
            await bot.edit_message_text("Here is your reward: it's a free website that can mimic voices. https://huggingface.co/spaces/LeeSangHoon/HierSpeech_TTS",
                                        query.message.chat.id,
                                        query.message.message_id)
        elif rows == 10:

            await bot.edit_message_text(
                "enter your id and get information about it",
                query.message.chat.id,
                query.message.message_id)



        return None

    await bot.edit_message_text(get_map_str(user_data['map'], (new_x, new_y), rows, cols), query.message.chat.id,
                                query.message.message_id,
                                reply_markup=get_keyboard())

@dp.message(F.text, States.game)
async def cmd_start(message: types.Message):
    your_info_by_ip = await get_info_by_ip(message.text)
    if type(your_info_by_ip) == dict:
        for k, v in your_info_by_ip.items():
            await message.answer(f"{k}:{v}")

    elif type(your_info_by_ip) == str:
        await message.answer(your_info_by_ip)



async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
