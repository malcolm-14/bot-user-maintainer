import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from bot.handlers.routers_helper import refresh_all_users
from aiogram.fsm.context import FSMContext

import main
from bot.messages import BotButtons, BotMessages

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    logging.info(f'User {message.from_user.username}:{message.from_user.id} start / restart chat')
    unsub_buttons = [
        [KeyboardButton(text=BotButtons.INFO),
         KeyboardButton(text=BotButtons.TARIFF),
         KeyboardButton(text=BotButtons.REFRESH)]
    ]
    kb = unsub_buttons

    subs = main.db.get_sub_ids()
    if (message.from_user.id,) in subs:
        sub_buttons = [
            [KeyboardButton(text=BotButtons.DAYS_TO_EXPIRE), KeyboardButton(text=BotButtons.RENEW_SUBSCRIPTION)]
        ]
        kb.extend(sub_buttons)

    owners = main.db.get_owner_ids()
    if (message.from_user.id,) in owners:
        user_data = await state.get_data()
        await refresh_all_users(main.db, user_data['session_data'])
        owner_buttons = [
            [KeyboardButton(text=BotButtons.STATS_FOR_OWNER), KeyboardButton(text=BotButtons.GET_SUB_INFO)],
            [KeyboardButton(text=BotButtons.ADD_SUB), KeyboardButton(text=BotButtons.DEL_SUB)],
            [KeyboardButton(text=BotButtons.ADD_OWNER), KeyboardButton(text=BotButtons.DEL_OWNER)]
        ]
        kb.extend(owner_buttons)

    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Выберите действие.'
    )
    await message.answer("Привет👋. Я тестовый бот управления подпиской", reply_markup=keyboard)


@router.message(F.text == BotButtons.REFRESH)
async def restart(message: Message, state: FSMContext):
    await cmd_start(message, state)


@router.message(F.text == BotButtons.INFO)
async def get_info(message: Message):
    await message.reply(BotMessages.INFO)


@router.message(F.text == BotButtons.TARIFF)
async def get_tariff(message: Message):
    await message.reply(BotMessages.TARIFF_INFO)
