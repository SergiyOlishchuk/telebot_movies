from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from emoji import emojize

from config import TOKEN

storage = MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

class FSMYear(StatesGroup):
    years = State()

years = {}

movies_inline_keyboard = InlineKeyboardMarkup()
movies_inline_keyboard.add(InlineKeyboardButton('Повністю випадковий фільм', callback_data='movie all'))
movies_inline_keyboard.row(InlineKeyboardButton('Фільм за жанром', callback_data='movie genre'), InlineKeyboardButton('Фільм за роками', callback_data='movie year'))
movies_inline_keyboard.add(InlineKeyboardButton('Фільм за всіма параметрами', callback_data='movie special'))


genres = ['Комедії', 'Бойовики', 'Детективи', 'Арт-хаус', 'Мелодрами', 'Трилери', 'Жахи', 'Мюзикли', 'Вестерни', 'Пригоди', 'Спортивні', 'Фантастика', 'Кримінал', 'Драми', 'Короткометражні', 'Біографія', 'Військові', 'Історія', 'Документальні', '18+', 'Сімейні', 'Аніме', 'Дитячі', 'Екранізація', 'Анімація', 'Комікси', 'Фентезі']
genres_btns = [InlineKeyboardButton(genre, callback_data=f'genre {genre}') for genre in genres]
genres_inline_keyboard = InlineKeyboardMarkup()

for i in range(0, len(genres_btns), 3):
    genres_inline_keyboard.row(*genres_btns[i:i+3])

genres_inline_keyboard.add(InlineKeyboardButton('Готово', callback_data='genre ready'))

selected_genres = {}
genres_text = 'Виберіть протрібні вам жанри'

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
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{call.message.text}\n\nФільм за роком')

    await FSMYear.years.set()
    await bot.send_message(call.message.chat.id, 'Введіть потрібні роки через кому')

@dp.message_handler(Text(equals='відміна', ignore_case=True), state='*')
async def cancel_year_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer('OK')

@dp.message_handler(content_types=['text'], state=FSMYear.years)
async def process_years(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['years'] = message.text
    
    async with state.proxy() as data:
        years[message.from_user.id] = [el.strip() for el in data['years'].split(',')]
    
    await state.finish()

    await bot.send_message(message.from_user.id, 'Дякую!')
    await bot.send_message(message.from_user.id, str(years[message.from_user.id]))

@dp.callback_query_handler(lambda c: c.data and c.data == 'movie genre')
async def process_callback_movie_year(call: types.CallbackQuery):
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{call.message.text}\n\nФільм за жанром')

    await bot.send_message(call.message.chat.id, genres_text, reply_markup=genres_inline_keyboard)

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