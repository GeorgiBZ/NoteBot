from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import database
import asyncio
import datetime
import sqlite3
import logging

#Второй коммит

# Создаем база данных
database.create_table()

# Указываем токен бота
TOKEN = "7436005603:AAE1vrv7BmmYRXPeGrdv8aht2-CnI0Q4-0A"

# Создаем объект бота
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Определяем состояния записи
class States(StatesGroup):
    waiting_for_time = State()
    waiting_for_note = State()

# Определяем состояния удаления
class DeleteNoteState(StatesGroup):
    waiting_for_delete = State()

# Определяем обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=get_keyboard(1))

# Функция для получения клавиатуры с кнопками
def get_keyboard(st):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if st == 1:
        keyboard.add("Список заметок")
        keyboard.add("Добавить заметку")
    if st == 2:
        keyboard.add("Список заметок")
        keyboard.add("Добавить заметку")
        keyboard.add("Удалить заметку")
    if st == 3:
        keyboard.add("Отмена")
    return keyboard

# Определяем обработчик команды "Добавить заметку"
@dp.message_handler(lambda message: message.text == "Добавить заметку")
async def add_note_start(message: types.Message):
    await message.answer("🗓 Введите время в формате *ГГГГ-ММ-ДД ЧЧ:ММ*:", parse_mode = 'Markdown', reply_markup=get_keyboard(3))
    await States.waiting_for_time.set()

# Определяем обработчик даты
@dp.message_handler(state=States.waiting_for_time)
async def process_datetime(message: types.Message, state: FSMContext):
    global datetime_str
    try:
        datetime_str = message.text
        datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
        await message.answer(f"💬 Введите текст заметки:")
        await States.waiting_for_note.set()
    except ValueError:
        if datetime_str == 'Отмена':
            await state.finish()
            await message.answer("❌ Действие отменено", reply_markup=get_keyboard(1))
        else:
            await message.answer("❌ Некорректный формат даты и времени. Пожалуйста, используйте формат *ГГГГ-ММ-ДД ЧЧ:ММ*", parse_mode = 'Markdown')

# Определяем обработчик текста заметки
@dp.message_handler(state=States.waiting_for_note)
async def process_note(message: types.Message, state: FSMContext):
    note_text = message.text
    
    try:
        database.add_note(
            user_id = message.from_user.id,
            datetime = datetime_str,
            note = note_text
        )
        await message.answer(f"✅ *Заметка сохранена:* {note_text}\n*Дата и время:* {datetime_str}", parse_mode = 'Markdown', reply_markup=get_keyboard(1))
    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении заметки: {e}", reply_markup=get_keyboard(1))
        print(f"❌ Ошибка при сохранении заметки: {e}")

    await state.finish()

# Определяем обработчик команды "Список заметок"
@dp.message_handler(lambda message: message.text == "Список заметок")
async def list_notes(message: types.Message):
    notes = database.get_notes(message.from_user.id)
    if notes:
        response = "\n".join([f"{id}) *Дата и время:* {datetime} *Текст:* {note}" for id, datetime, note in notes])
        await message.answer(response, parse_mode = 'Markdown', reply_markup=get_keyboard(2))
    else:
        response = "🤷‍ У вас нет сохраненных заметок."
        await message.answer(response, parse_mode = 'Markdown', reply_markup=get_keyboard(1))
    

# Определяем обработчик команды "Удалить заметку"
@dp.message_handler(lambda message: message.text == "Удалить заметку")
async def delete_note_start(message: types.Message):
    await message.answer("⚠️ Введите номер заметки, которую хотите удалить:", reply_markup=get_keyboard(3))
    await DeleteNoteState.waiting_for_delete.set()

# Определяем обработчик удаления заметки
@dp.message_handler(state=DeleteNoteState.waiting_for_delete)
async def process_delete_note_id(message: types.Message, state: FSMContext):
    note_id = message.text
    if note_id.isdigit():
        try:
            database.delete_note(int(note_id))
            await message.answer(f"🗑 Заметка с номером {note_id} удалена.", reply_markup=get_keyboard(1))
            database.rebuild_ids()
            await state.finish()
        except Exception as e:
            await message.answer(f"❌ Ошибка при удалении заметки: {e}", reply_markup=get_keyboard(1))
            print(f"❌ Ошибка при удалении заметки: {e}")
    else:
        if note_id == 'Отмена':
            await state.finish()
            await message.answer("❌ Действие отменено", reply_markup=get_keyboard(1))
        else:
            await message.answer("❌ Номер заметки должно быть числом. Пожалуйста, попробуйте снова.", reply_markup=get_keyboard(3))

async def notify_users():
    while True:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        with sqlite3.connect('notes.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, note FROM notes WHERE datetime = ?", (now,))
            notes = cursor.fetchall()
            for user_id, note in notes:
                await bot.send_message(user_id, f"🔔*Напоминание:* {note}", parse_mode = 'Markdown')
            cursor.execute("DELETE FROM notes WHERE datetime = ?", (now,))
            conn.commit()
            database.rebuild_ids()
        await asyncio.sleep(60)

# Запускаем бота
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(notify_users())
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
        except Exception as e:
            logging.error(f"Error in polling: {e}")
            asyncio.sleep(5)