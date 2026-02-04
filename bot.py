# src/bot.py — финальная версия для Render.com

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ТВОИ ДАННЫЕ
BOT_TOKEN = '8343019428:AAEBBuTcZo_nhUtDO3hFV1lV8eVQI4psQP4'
ADMIN_ID  = 8365937716

bot = Bot(token=BOT_TOKEN)  # без прокси — на Render работает
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    model = State()
    contact = State()

main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Оставить заявку", callback_data="leave_request")]
])

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Привет! Я бот канала @naveska_rus\n\n"
        "Подберём навесное оборудование под вашу технику за 5 минут!\n"
        "Гидромолоты, бетоноломы, обрубщики свай, вибропогружатели и многое другое.\n\n"
        "Нажми кнопку ниже, чтобы оставить заявку:",
        reply_markup=main_kb
    )

@dp.callback_query(lambda c: c.data == "leave_request")
async def start_request(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Отлично! Напишите модель вашей техники\n"
        "(например: Hitachi ZX200, Bobcat S650, экскаватор 20 т и т.д.)"
    )
    await state.set_state(Form.model)
    await callback.answer()

@dp.message(Form.model)
async def process_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer(
        "Теперь укажите ваш контакт для связи\n"
        "(телефон, Telegram @ник, WhatsApp):"
    )
    await state.set_state(Form.contact)

@dp.message(Form.contact)
async def process_contact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    model = data.get('model', 'не указано')
    contact = message.text

    await bot.send_message(
        ADMIN_ID,
        f"НОВАЯ ЗАЯВКА!\n\n"
        f"Модель техники: {model}\n"
        f"Контакт: {contact}\n"
        f"От пользователя: @{message.from_user.username or 'нет ника'} "
        f"(ID: {message.from_user.id})"
    )

    await message.answer(
        "Спасибо! Заявка отправлена.\n"
        "Менеджер свяжется с вами в ближайшие 5–15 минут.\n\n"
        "Пока ждёте — подпишитесь на канал с видео работы техники и ценами:\n"
        "👉 @naveska_rus"
    )

    await state.clear()

async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())
