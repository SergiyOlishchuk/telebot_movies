from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import DataBase

from emoji import emojize

from config import TOKEN

storage = MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

db = DataBase()
selected_movies = {}

movies_inline_keyboard = InlineKeyboardMarkup()
movies_inline_keyboard.add(InlineKeyboardButton('Повністю випадковий фільм', callback_data='movie all'))
movies_inline_keyboard.row(InlineKeyboardButton('Фільм за жанром', callback_data='movie genre'), InlineKeyboardButton('Фільм за роками', callback_data='movie year'))
movies_inline_keyboard.add(InlineKeyboardButton('Фільм за всіма параметрами', callback_data='movie special'))


genres = db.get_genres()
genres_btns = [InlineKeyboardButton(genre, callback_data=f'genre {genre}') for genre in genres]
genres_inline_keyboard = InlineKeyboardMarkup()

for i in range(0, len(genres_btns), 3):
    genres_inline_keyboard.row(*genres_btns[i:i+3])

genres_inline_keyboard.add(InlineKeyboardButton('Готово', callback_data='genre ready'))

selected_genres = {}
genres_text = 'Виберіть протрібні вам жанри'

years = db.get_years()
years_btns = [InlineKeyboardButton(year, callback_data=f'year {year}') for year in years]
years_inline_keyboard = InlineKeyboardMarkup()

for i in range(0, len(years_btns), 5):
    years_inline_keyboard.row(*years_btns[i:i+5])

years_inline_keyboard.add(InlineKeyboardButton('Готово', callback_data='year ready'))

selected_years = {}
years_text = 'Виберіть потрібні вам роки'

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply('Привіт\nЯ бот для вибору фільмів\nНапиши /help, щоб дізнатися мої команди')

@dp.message_handler(commands=['help'])
async def start_command(message: types.Message):
    await message.reply(emojize('Поки що тут нічого немає :smiling_face_with_tear:'))

@dp.message_handler(commands=['find_movie'])
async def find_movie(message: types.Message):
    await bot.send_message(message.from_user.id, 'Що конкретно вам потрібно?', reply_markup=movies_inline_keyboard)

@dp.callback_query_handler(lambda c: c.data and c.data == 'movie year', state=None)
async def process_callback_movie_year(call: types.CallbackQuery):
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{call.message.text}\n\nФільм за за роком')

    selected_years[call.from_user.id] = []
    
    await bot.send_message(call.message.chat.id, years_text, reply_markup=years_inline_keyboard)



@dp.callback_query_handler(lambda c: c.data and c.data == 'movie genre')
async def process_callback_movie_year(call: types.CallbackQuery):
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{call.message.text}\n\nФільм за жанром')

    selected_genres[call.from_user.id] = []

    await bot.send_message(call.message.chat.id, genres_text, reply_markup=genres_inline_keyboard)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('year'))
async def process_genres(call: types.CallbackQuery):
    call_year = call.data.split(' ', maxsplit=2)[-1]

    user_id = call.from_user.id

    if call_year == 'ready':
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        if len(selected_years[user_id]) > 0:
            selected_movies[user_id] = db.get_random_movies(1, years=tuple(selected_years[user_id]))[0] 
            await bot.send_message(user_id, f'Назва: {selected_movies[user_id][0]}\nЖанр: {selected_movies[user_id][1]}\nРік: {selected_movies[user_id][2]}\nПосилання: {selected_movies[user_id][3]}')
            del selected_movies[user_id]
        else:
            await bot.send_message(call.message.chat.id, 'Ви не вибрали жанри(')

    else:
        if call_year in selected_years[user_id]:
            selected_years[user_id].remove(call_year)
        else:
            selected_years[user_id].append(call_year)
        
        new_years_text = years_text + '\nВибрані вами роки: '
        for selected in selected_years[user_id]:
            new_years_text += selected + ', '
        new_years_text = new_years_text[:-2]
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_years_text, reply_markup=years_inline_keyboard)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('genre'))
async def process_genres(call: types.CallbackQuery):
    call_genre = call.data.split(' ', maxsplit=2)[-1]

    user_id = call.from_user.id

    if call_genre == 'ready':
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        if len(selected_genres[user_id]) > 0:
            selected_movies[user_id] = db.get_random_movies(1, genres=tuple(selected_genres[user_id]))[0] 
            await bot.send_message(user_id, f'Назва: {selected_movies[user_id][0]}\nЖанр: {selected_movies[user_id][1]}\nРік: {selected_movies[user_id][2]}\nПосилання: {selected_movies[user_id][3]}')
            del selected_movies[user_id]
        else:
            await bot.send_message(call.message.chat.id, 'Ви не вибрали жанри(')

    else:
        if call_genre in selected_genres[user_id]:
            selected_genres[user_id].remove(call_genre)
        else:
            selected_genres[user_id].append(call_genre)
        
        new_genres_text = genres_text + '\nВибрані вами жанри: '
        for selected in selected_genres[user_id]:
            new_genres_text += selected + ', '
        new_genres_text = new_genres_text[:-2]
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_genres_text, reply_markup=genres_inline_keyboard)

@dp.callback_query_handler(lambda c: c.data and c.data == 'movie all')
async def process_callback_movie_all(call: types.CallbackQuery):
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{call.message.text}\n\nВипадковий фільм')

    user_id = call.from_user.id
    selected_movies[user_id] = db.get_random_movies(1)[0]
    await bot.send_message(user_id, f'Назва: {selected_movies[user_id][0]}\nЖанр: {selected_movies[user_id][1]}\nРік: {selected_movies[user_id][2]}\nПосилання: {selected_movies[user_id][3]}')
    del selected_movies[user_id]

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('movie'))
async def process_callback_movie(call: types.CallbackQuery):
    type = call.data.split(' ')[-1]

    message_end = {
        'all' : 'Повністю випадковий фільм',
        'genre' : 'Фільм за жанром',
        'year' : 'Фільм за роком',
        'special' : 'Фільм за всіма параметрами'
    }
 
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{call.message.text}\n\n{ message_end[type] }')



@dp.message_handler(commands=['random_movie'])
async def random_movie_command(message: types.Message):
    await bot.send_message(message.from_user.id, 'Поки що це просто заглушка')

@dp.message_handler()
async def echo(message: types.Message):
    await bot.send_message(message.from_user.id, message.text)

if __name__ == '__main__':
    executor.start_polling(dp)