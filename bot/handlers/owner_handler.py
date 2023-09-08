import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from dbcontroller import ExistsError
from bot.messages import BotMessages, BotButtons
from .routers_helper import get_user_id
from bot import permissions, bot_main

router = Router()


# -- Start add subscriber section
class AddSubscriberForm(StatesGroup):
    waiting_for_username = State()
    waiting_for_start_sub_days = State()


@router.message(F.text == BotButtons.ADD_SUB)
@permissions.is_owner
async def sub_add(message: Message, state: FSMContext):
    await message.reply(f"Введите username пользователя в телеграм для добавления в подписчики.")
    await state.set_state(AddSubscriberForm.waiting_for_username)


@router.message(AddSubscriberForm.waiting_for_username)
async def sub_username_chosen(message: Message, state: FSMContext):
    username = message.text
    try:
        user_id = await get_user_id(username)
    except ValueError as ex:
        await message.answer(text=f"Похоже, пользователя с username '{username}' не существует.")
        await state.clear()
        return

    await state.update_data(username=message.text)
    await state.update_data(tg_id=user_id)

    await message.answer(text="Отлично. Задайте начальное количество дней подписки (-1: бессрочно)")
    await state.set_state(AddSubscriberForm.waiting_for_start_sub_days)


@router.message(AddSubscriberForm.waiting_for_start_sub_days)
async def sub_start_subscription_days_chosen(message: Message, state: FSMContext):
    await state.update_data(start_sub_days=message.text)
    user_data = await state.get_data()
    username = user_data['username']
    start_sub_days = user_data['start_sub_days']
    user_id = user_data['tg_id']

    await message.reply(f"Добавление {username} в таблицу подписчиков...")
    bot_main.db.add_to_sub_table(user_id, username, start_sub_days)

    await message.reply(f"Пользователь {username} id: {user_id} успешно добавлен таблицу.")
    await state.clear()
# -- End add subscriber section


# -- Start add owner section
class AddOwnerForm(StatesGroup):
    waiting_for_username = State()


@router.message(F.text == BotButtons.ADD_SUB)
@permissions.is_owner
async def owner_add(message: Message, state: FSMContext):
    await message.reply(f"Введите *username* пользователя в телеграм для добавления в владельцы")
    await state.set_state(AddOwnerForm.waiting_for_username)


@router.message(AddOwnerForm.waiting_for_username)
async def owner_username_chosen(message: Message, state: FSMContext):
    username = message.text
    try:
        user_id = await get_user_id(username)
    except ValueError as ex:
        await message.answer(text=f"Похоже, пользователя с username '{username}' не существует.")
        await state.clear()
        return

    await message.reply(f"Добавление {username} в таблицу владельцев...")
    bot_main.db.add_to_sub_table(user_id, username)

    await message.reply(f"Пользователь {username} id: {user_id} успешно добавлен таблицу.")
    await state.clear()
# -- End add owner section


@router.message(F.text == BotButtons.STATS_FOR_OWNER)
@permissions.is_owner
async def get_global_stats(message: Message):
    subs = bot_main.db.get_all_subs()
    subs_string = '[TG ID]     NICKNAME | DAYS | STATUS\n'
    for sub in subs:
        sub_str = '%10 %20 %5 %7'.format(sub[0], sub[1], sub[2], sub[3])
        subs_string += sub_str

    await message.reply(subs_string)

# -- Start sub info section
class GetSubStatsForm(StatesGroup):
    waiting_for_username = State()


@router.message(F.text == BotButtons.GET_SUB_INFO)
@permissions.is_owner
async def get_sub_info(message: Message, state: FSMContext):
    await message.reply(f"Введите *username* пользователя в телеграм для получения статистики")
    await state.set_state(GetSubStatsForm.waiting_for_username)


@router.message(GetSubStatsForm.waiting_for_username)
async def sub_username_chosen(message: Message, state: FSMContext):
    username = message.text
    try:
        days, status = bot_main.db.get_sub_stats(username)
    except ExistsError:
        await message.reply(f"Пользователя {username} не существует в таблице (или он сменил username)")
        await state.clear()
        return

    await message.reply(f"{username} | Статус: {status} | Дней: {days}")
    await state.clear()
# -- End sub stats section


@router.message(F.text == BotButtons.DEL_SUB)
@permissions.is_owner
async def delete_sub(message: Message):
    await message.reply(f"Пока невозможно удалить подписчика из системы")


@router.message(F.text == BotButtons.DEL_SUB)
@permissions.is_owner
async def delete_owner(message: Message):
    await message.reply(f"Пока невозможно удалить подписчика из системы")
