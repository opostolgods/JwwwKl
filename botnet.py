import sqlite3
import telethon
from telethon import TelegramClient, events, sync, functions
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from telethon.tl.types import InputReportReasonSpam, InputReportReasonFake, InputReportReasonViolence, InputReportReasonChildAbuse, InputReportReasonOther
from telethon.tl.functions.messages import ReportSpamRequest
import asyncio
import telebot
from telebot import types
from telethon import types as telethon_types
import time
import os
import shutil
import random
from datetime import datetime, timedelta
from pyCryptoPayAPI import pyCryptoPayAPI
import config
from telethon.tl.types import PeerUser

while True:
    try:
        reasons = [
            InputReportReasonSpam(),
            InputReportReasonFake(),
            InputReportReasonViolence(),
            InputReportReasonChildAbuse(),
            InputReportReasonOther()
        ]

        API = "7253894752:AAF50Bxqn7l9BbVFzem2QECcjmNmBouW88A"

        bot = telebot.TeleBot(config.TOKEN)
        bot_name = config.bot_name
        bot_logs = config.bot_logs
        bot_channel_link = config.bot_channel_link
        bot_admin = config.bot_admin
        bot_documentation = config.bot_documentation
        bot_reviews = config.bot_reviews
        bot_works = config.bot_works
        crypto = pyCryptoPayAPI(api_token=config.CRYPTO)
        session_folder = 'sessions'
        sessions = [f.replace('.session', '') for f in os.listdir(session_folder) if f.endswith('.session')]
        last_used = {}

        subscribe_1_day = config.subscribe_1_day
        subscribe_7_days = config.subscribe_7_days
        subscribe_14_days = config.subscribe_14_days
        subscribe_30_days = config.subscribe_30_days
        subscribe_365_days = config.subscribe_365_days
        subscribe_infinity_days = config.subscribe_infinity_days

        menu = types.InlineKeyboardMarkup(row_width=2)
        profile = types.InlineKeyboardButton("👤 Профиль", callback_data='profile')
        doc = types.InlineKeyboardButton("⭐️ Канал", url=f'{bot_documentation}')
        shop = types.InlineKeyboardButton("🛒 Подписки", callback_data='shop')
        snoser = types.InlineKeyboardButton("🌐 отправить пицу", callback_data='snoser')
        menu.add(profile)
        menu.add(doc, shop)
        menu.add(snoser)

        back_markup = types.InlineKeyboardMarkup(row_width=2)
        back = types.InlineKeyboardButton("🔙 Назад", callback_data='back')
        back_markup.add(back)

        channel_markup = types.InlineKeyboardMarkup(row_width=2)
        channel = types.InlineKeyboardButton(f"⚡️ {bot_name} - канал", url=f'{bot_channel_link}')
        channel_markup.add(channel)

        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        add_subsribe = types.InlineKeyboardButton("Выдать подписку", callback_data='add_subsribe')
        clear_subscribe = types.InlineKeyboardButton("Забрать подписку", callback_data='clear_subscribe')
        send_all = types.InlineKeyboardButton("Рассылка", callback_data='send_all')
        admin_markup.add(add_subsribe, clear_subscribe)
        admin_markup.add(send_all)

        shop_markup = types.InlineKeyboardMarkup(row_width=2)
        sub_1 = types.InlineKeyboardButton(f"🔹 1 день - {subscribe_1_day}$", callback_data='sub_1')
        sub_2 = types.InlineKeyboardButton(f"🔹 7 дней - {subscribe_7_days}$", callback_data='sub_2')
        sub_4 = types.InlineKeyboardButton(f"🔹 30 дней - {subscribe_30_days}$", callback_data='sub_4')
        sub_6 = types.InlineKeyboardButton(f"🔹 навсегда - {subscribe_infinity_days}$", callback_data='sub_6')
        shop_markup.add(sub_1, sub_2)
        shop_markup.add(sub_4, sub_6)
        shop_markup.add(back)

        def check_user_in_db(user_id):
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result is not None

        def extract_username_and_message_id(message_url):
            try:
                path = message_url[len('https://t.me/'):].split('/')
                print(path)
                if len(path) == 2:
                    chat_username = path[0]
                    message_id = int(path[1])
                    return chat_username, message_id
                else:
                    raise ValueError("Неверный формат URL")
            except Exception as e:
                print(f"Ошибка при разборе URL: {e}")
                raise ValueError("Неверный формат URL")

        async def main(chat_username, message_id, user):
            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            valid = 0
            ne_valid = 0
            flood = 0
            reports = 0
            for session in sessions:
                api_id, api_hash = "20401021", "7fa6c7f62816334c230cebf77c565c3d"
                random_reason = random.choice(reasons)
                try:
                    session_file = os.path.join("sessions", session + ".session")
                    session_path = os.path.join("sessions", session)
                    
                    if not os.path.exists(session_file):
                        print(f"Сессия {session} не найдена")
                        ne_valid += 1
                        continue
                        
                    client = TelegramClient(
                        session_path,
                        int(api_id),
                        api_hash,
                        system_version='4.16.30-vxCUSTOM',
                        sequential_updates=True
                    )

                    try:
                        await client.connect()
                        if not await client.is_user_authorized():
                            print(f"Сессия {session} не авторизована")
                            ne_valid += 1
                            await client.disconnect()
                            continue
                            
                        # Получаем информацию о чате
                        chat = await client.get_entity(chat_username)
                        
                        # Отправляем жалобу, используя ReportSpam
                        await client(functions.messages.ReportSpamRequest(
                            peer=chat
                        ))
                        reports += 1
                        await client.disconnect()
                    except FloodWaitError as e:
                        flood = flood + 1
                        print(f'Flood wait error ({session}): {e}')
                        await client.disconnect()
                    except Exception as e:
                        if "chat not found" in str(e):
                            bot.send_message(user, "🚫 *Произошла ошибка при получении сообщения!*", parse_mode="Markdown", reply_markup=back_markup)
                            await client.disconnect()
                            return
                        elif "object has no attribute 'from_id'" in str(e):
                            bot.send_message(user, "🚫 *Произошла ошибка при получении сообщения!*", parse_mode="Markdown", reply_markup=back_markup)
                            await client.disconnect()
                            return
                        elif "database is locked" in str(e):
                            connect.close()
                            continue
                        else:
                            ne_valid += 1
                            print(f'Ошибка ({session}): {e}')
                            await client.disconnect()
                            continue
                except Exception as e:
                    print(f'Ошибка ({session}): {e}')
                    continue

            user_markup = types.InlineKeyboardMarkup(row_width=2)
            user_profile = types.InlineKeyboardButton(f"{user}", url=f'tg://openmessage?user_id={user}')
            user_markup.add(user_profile)
            bot.send_message(bot_logs, f"⚡️ *Произошел запуск бота:*\n\n*ID:* `{user}`\n*Ссылка: https://t.me/{chat_username}/{message_id}*\n\n🔔 *Информация о сессиях:*\n⚡️ Валидные: *{reports}*\n⚡️ *Не валидные: {ne_valid}*\n⚡️ *FloodError: {flood}*", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=user_markup)
            bot.send_message(user, f"⚡️ *Жалобы успешно поданы!*  \n\n🟢 *Валид:* `{reports}`  \n🔴 *Не валид:* `{ne_valid}`", parse_mode="Markdown", reply_markup=back_markup)
            connect.close()

        @bot.message_handler(commands=['start'])
        def welcome(message):
            connect = sqlite3.connect("users.db")
            cursor = connect.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                user_id BIGINT,
                subscribe DATETIME
            )""")
            people_id = message.chat.id
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (people_id,))
            data = cursor.fetchone()
            if data is None:
                cursor.execute("INSERT INTO users VALUES(?, ?);", (people_id, "1999-01-01 20:00:00"))
                connect.commit()
                bot.send_message(message.chat.id, "👋 *Привет!*", reply_markup=channel_markup, parse_mode="Markdown")
            bot.send_message(message.chat.id, f'🍕 *{bot_name}* — _бот для быстрой доставки пиццы._\n\n⚡️ *Админ: {bot_admin}*\n⭐️ *Отзывы:* [ТЫК]({bot_reviews})\n🔥 *Работы:* [ТЫК]({bot_works})', parse_mode="Markdown", reply_markup=menu)
            connect.close()

        @bot.callback_query_handler(lambda c: c.data and c.data.startswith('sub_'))
        def handle_subscription(callback_query: types.CallbackQuery):
            try:
                user_id = callback_query.from_user.id
                user_first_name = callback_query.from_user.first_name 
                if not check_user_in_db(user_id):
                    bot.send_message(user_id, "*❗️ Вы блокировали бота! Пропишите /start*", parse_mode="Markdown")

                subscription_type = callback_query.data.split('_')[1]

                if subscription_type == "1":
                    invoice = crypto.create_invoice(asset='USDT', amount=subscribe_1_day)
                    sub_days = "1"
                    amount = subscribe_1_day
                if subscription_type == "2":
                    invoice = crypto.create_invoice(asset='USDT', amount=subscribe_7_days)
                    sub_days = "7"
                    amount = subscribe_7_days
                if subscription_type == "3":
                    invoice = crypto.create_invoice(asset='USDT', amount=subscribe_14_days)
                    sub_days = "14"
                    amount = subscribe_14_days
                if subscription_type == "4":
                    invoice = crypto.create_invoice(asset='USDT', amount=subscribe_30_days)
                    sub_days = "30"
                    amount = subscribe_30_days
                if subscription_type == "5":
                    invoice = crypto.create_invoice(asset='USDT', amount=subscribe_365_days)
                    sub_days = "365"
                    amount = 35
                if subscription_type == "6":
                    invoice = crypto.create_invoice(asset='USDT', amount=subscribe_infinity_days)
                    sub_days = "3500"
                    amount = subscribe_infinity_days

            
                pay_url = invoice['pay_url']
                invoice_id = invoice['invoice_id']
                pay_check = types.InlineKeyboardMarkup(row_width=2)
                pay_url = types.InlineKeyboardButton("💸 Оплатить пиццу", url=pay_url)
                check = types.InlineKeyboardButton("🔍 Проверить платеж", callback_data=f'check_status_{invoice_id}_{subscription_type}_{sub_days}')
                pay_check.add(pay_url, check)
                pay_check.add(back)
                bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                    text=f'⭐️ *Оплата подписки {bot_name}* ⭐️\n\n🛒*Подписка на {sub_days} дней*\n💳 *Цена:* `{amount}$`\n\n✨ *Спасибо за покупку!*',
                    parse_mode="Markdown", reply_markup=pay_check)
            except:
                pass

        @bot.callback_query_handler(lambda c: c.data and c.data.startswith('check_status_'))
        def check_status_callback(callback_query: types.CallbackQuery):
            try:
                user_id = callback_query.from_user.id
                if not check_user_in_db(user_id):
                    bot.send_message(user_id, "*❗️ Вы блокировали бота! Пропишите /start*", parse_mode="Markdown")
                else:
                    parts = callback_query.data.split('_')
                    if len(parts) < 4:
                        callback_query.answer("Неверный формат данных. Пожалуйста, попробуйте еще раз.")
                        return
                    invoice_id = parts[2]
                    sub_days = parts[4]
                    check_status(callback_query, invoice_id, sub_days)
            except:
                pass

        def check_status(callback_query: types.CallbackQuery, invoice_id: str, sub_days):
            try:
                user_id = callback_query.from_user.id
                if not check_user_in_db(user_id):
                    bot.send_message(user_id, "*❗️ Вы блокировали бота! Пропишите /start*", parse_mode="Markdown")
                else:
                    ID = callback_query.from_user.id
                    connect = sqlite3.connect('users.db')
                    cursor = connect.cursor()
                    subscribe_str = cursor.execute("SELECT subscribe FROM users WHERE user_id = ?", (ID,)).fetchone()
                    if subscribe_str is None:
                        bot.send_message(callback_query.message.chat.id, "❌ *Не удалось найти данные пользователя.*", parse_mode="Markdown")
                        return
                    subscribe_str = subscribe_str[0]
                    subsribe = datetime.strptime(subscribe_str, "%Y-%m-%d %H:%M:%S")
                    old_invoice = crypto.get_invoices(invoice_ids=invoice_id)
                    status_old_invoice = old_invoice['items'][0]['status']
                    subscription_type = old_invoice['items'][0]['amount']
                    if status_old_invoice == "paid":
                        bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                            text=f'⭐️ *Оплачен!*',
                            parse_mode="Markdown", reply_markup=back_markup)
                        bot.send_message(callback_query.message.chat.id, "✨ *Оплата получена!*", parse_mode="Markdown")
                        try:
                            days = int(sub_days)
                            new_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
                            cursor.execute("UPDATE users SET subscribe = ? WHERE user_id = ?", (new_date, ID))
                            connect.commit()
                            # Клава
                            subscribe_markup = types.InlineKeyboardMarkup(row_width=1)
                            user_button = types.InlineKeyboardButton(f"Пользователь: {ID}", url=f'tg://openmessage?user_id={ID}')
                            subscribe_markup.add(user_button)
                            bot.send_message(bot_logs, f'⚡️ *Пользователь* `{ID}` *оплатил подписку (теперь действует до* `{new_date}`*)*', parse_mode="Markdown", reply_markup=subscribe_markup)
                            connect.close()
                        except Exception as e:
                            connect.close()
                    else:
                        bot.send_message(callback_query.message.chat.id, "🚫 *Оплата не получена!*", parse_mode="Markdown")
                        connect.close()
            except:
                pass

        @bot.callback_query_handler(func=lambda call: True)
        def callback_inline(call):
            try:
                user_id = call.from_user.id
                if not check_user_in_db(user_id):
                    bot.send_message(user_id, "*❗️ Вы блокировали бота! Пропишите /start*", parse_mode="Markdown")
                else:
                    connect = sqlite3.connect('users.db')
                    cursor = connect.cursor()
                    user_id = call.from_user.id
                    subscribe_str = cursor.execute("SELECT subscribe FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
                    subsribe = datetime.strptime(subscribe_str, "%Y-%m-%d %H:%M:%S")
                    if call.message:
                        if call.data == 'snoser':
                            if subsribe < datetime.now():
                                bot.send_message(call.message.chat.id, '⚡️ *Ваша подписка истекла!* \n\n🚫 *Для использования доставки пиццы купите подписку.*', parse_mode="Markdown")
                            else:
                                if user_id in last_used and (datetime.now() - last_used[user_id]) < timedelta(minutes=5):
                                    remaining_time = timedelta(minutes=5) - (datetime.now() - last_used[user_id])
                                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text=f'🚫 *Ждите {remaining_time.seconds} секунд до следующей отправки жалоб!*',
                                                  parse_mode="Markdown", reply_markup=back_markup)
                                    return
                                last_used[user_id] = datetime.now()
                                x = bot.send_message(call.message.chat.id, f'⚡️ *Введите ссылку на нарушение:*', parse_mode="Markdown")
                                bot.register_next_step_handler(x, BotNetStep1)
                        elif call.data == 'back':
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'♨️ *{bot_name}* — _бот для массовой отправки жалоб._\n\n✨ *Админ: {bot_admin}*\n✨ *Работы:* [Works]({bot_works})\n✨ *Отзывы:* [Reviews]({bot_reviews})',
                                parse_mode="Markdown", reply_markup=menu)
                        elif call.data == 'profile':
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'👤 *Ваш профиль* \n\n🆔 *ID:* `{user_id}`\n🕐 *Текущее время:* `{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}`\n💰 *Подписка до:* `{subsribe}`\n\n🔐 _Не забудьте вовремя обновить свою подписку!_',
                                parse_mode="Markdown", reply_markup=back_markup)
                        elif call.data == 'shop':
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=(f"⚡️ *{bot_name} Price List* ⚡️\n\n🔹 *1 дeнь* — `{subscribe_1_day}$`\n🔹 *7 дней* — `{subscribe_7_days}$`\n🔹 *30 дней* — `{subscribe_30_days}$`\n🔹 *Навсегда* — `{subscribe_infinity_days}$`\n\n💼 *Для покупки за рубли: {bot_admin}*\n\n⚡️ *Работаем быстро!*"), parse_mode="Markdown", reply_markup=shop_markup, disable_web_page_preview = True)
                        elif call.data == 'add_subsribe':
                            msg = bot.send_message(call.message.chat.id, '*⚡️  ADD SUBSCRIBE  ⚡️*\n\n*Введите ID:*', parse_mode="Markdown")
                            bot.register_next_step_handler(msg, add_subsribe1) 
                        elif call.data == 'clear_subscribe':
                            msg = bot.send_message(call.message.chat.id, '*⚡️  CLEAR SUBSCRIBE  ⚡️*\n\n*Введите ID:*', parse_mode="Markdown")
                            bot.register_next_step_handler(msg, clear_subscribe)
                        elif call.data == 'send_all':
                            msg = bot.send_message(call.message.chat.id, '*⚡️  SEND ALL  ⚡️*\n\n*Введите текст (без картинок, эмодзи тг премиум):*', parse_mode="Markdown")
                            bot.register_next_step_handler(msg, sendall1)
            except:
                pass

        @bot.message_handler(commands=['admin'])
        def admin(message):
            if message.chat.id in config.ADMINS:
                bot.send_message(message.chat.id, "⚡️ *ADMIN PANEL* ⚡️",reply_markup=admin_markup, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "⚡️ *ADMIN PANEL* ⚡️\n\n_У вас нет прав!_", parse_mode="Markdown")

        def BotNetStep1(message):
            message_url = message.text
            user = message.from_user.id
            try:
                chat_username, message_id = extract_username_and_message_id(message_url)
                if chat_username and message_id:
                    bot.send_message(message.chat.id, '⚡️ *атака началась!\n\nПожалуйста, ожидайте.*', parse_mode="Markdown")
                    asyncio.run(main(chat_username, message_id, user))
                else:
                    bot.send_message(message.chat.id, '⚡️ *Неверная ссылка! Нужна ссылка на сообщение (https://t.me/XXX/YYY)!*', parse_mode="Markdown")
            except ValueError as e:
                print(f"Error parsing URL: {e}")
                bot.send_message(message.chat.id, '⚡️ *Неверная ссылка! Нужна ссылка на сообщение (https://t.me/XXX/YYY)!*', parse_mode="Markdown")
            except Exception as e:
                print(f"Unexpected error: {e}")
                bot.send_message(message.chat.id, '⚡️ *отправка жалоб еще идет.*', parse_mode="Markdown")

        def add_subsribe1(message):
            try:
                ID = int(message.text)
                msg2 = bot.send_message(message.chat.id, '*✞  ADD SUBSCRIBE  ✞*\n\n*Введите количество дней:*', parse_mode="Markdown")
                bot.register_next_step_handler(msg2, add_subsribe2, ID)
            except:
                bot.send_message(f'{ID}', f'⚡️ *Выдано!*', parse_mode="Markdown", reply_markup=back_markup)

        def add_subsribe2(message, ID):
            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            user_data = cursor.execute("SELECT subscribe FROM users WHERE user_id = ?", (ID,)).fetchone()
            if user_data is None:
                bot.send_message(message.chat.id, f'⚡️ *Ошибка!* Пользователь с ID `{ID}` не найден.', parse_mode="Markdown", reply_markup=back_markup)
                return
            subscribe_str = cursor.execute("SELECT subscribe FROM users WHERE user_id = ?", (ID,)).fetchone()[0]
            subsribe = datetime.strptime(subscribe_str, "%Y-%m-%d %H:%M:%S")
            try:
                days = int(message.text)
                new_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("UPDATE users SET subscribe = ? WHERE user_id = ?", (new_date, ID))
                connect.commit()
                bot.send_message(f'{ID}', f'⚡️ *Ваша подписка обновлена!: действует до* `{new_date}`.', parse_mode="Markdown")
                bot.send_message(message.chat.id, f'⚡️ *Вы обновили подписку* *(теперь действует до* `{new_date}`*) пользователю:* `{ID}`', parse_mode="Markdown", reply_markup=back_markup)
                #Клава
                subscribe_markup = types.InlineKeyboardMarkup(row_width=1)
                admin_id_button = types.InlineKeyboardButton(f"Админ: {message.chat.id}", url=f'tg://openmessage?user_id={message.chat.id}')
                user_button = types.InlineKeyboardButton(f"Пользователь: {ID}", url=f'tg://openmessage?user_id={ID}')
                subscribe_markup.add(admin_id_button, user_button)
                bot.send_message(bot_logs, f'⚡️ *Админ* `{message.chat.id}`*, обновил подписку (теперь действует до* `{new_date}`*) пользователю* `{ID}`', parse_mode="Markdown", reply_markup=subscribe_markup)
                connect.close()
            except Exception as e:
                bot.send_message(message.chat.id, f'⚡️ *Ошибка!*', parse_mode="Markdown", reply_markup=back_markup)
                connect.close()

        def clear_subscribe(message):
            try:
                ID = int(message.text)
                new_date = "1999-01-01 20:00:00"
                connect = sqlite3.connect('users.db')
                cursor = connect.cursor()
                user_data = cursor.execute("SELECT subscribe FROM users WHERE user_id = ?", (ID,)).fetchone()
                if user_data is None:
                    bot.send_message(message.chat.id, f'⚡️ *Ошибка!* Пользователь с ID `{ID}` не найден.', parse_mode="Markdown", reply_markup=back_markup)
                    connect.close()
                    return
                subscribe_str = cursor.execute("SELECT subscribe FROM users WHERE user_id = ?", (ID,)).fetchone()[0]
                subsribe = datetime.strptime(subscribe_str, "%Y-%m-%d %H:%M:%S")
                cursor.execute("UPDATE users SET subscribe = ? WHERE user_id = ?", (new_date, ID))
                connect.commit()
                bot.send_message(f'{ID}', f'⚡️ *Ваша подписка аннулирована!*', parse_mode="Markdown")
                bot.send_message(message.chat.id, f'⚡️ *Вы аннулировали подписку пользователю:* `{ID}`', parse_mode="Markdown", reply_markup=back_markup)
                #Клава
                subscribe_markup = types.InlineKeyboardMarkup(row_width=1)
                admin_id_button = types.InlineKeyboardButton(f"Админ: {message.chat.id}", url=f'tg://openmessage?user_id={message.chat.id}')
                user_button = types.InlineKeyboardButton(f"Пользователь: {ID}", url=f'tg://openmessage?user_id={ID}')
                subscribe_markup.add(admin_id_button, user_button)
                bot.send_message(bot_logs, f'⚡️ *Админ* `{message.chat.id}`* обновил подписку (аннулирована) пользователю* `{ID}`', parse_mode="Markdown", reply_markup=subscribe_markup)
                connect.close()
            except:
                bot.send_message(message.chat.id, f'⚡️ *Ошибка!*', parse_mode="Markdown", reply_markup=back_markup)
                connect.close()

        def sendall1(message):
            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            users = cursor.execute(f"SELECT user_id from users").fetchall()
            try:
                x = 0
                y = 0
                text = message.text
                bot.send_message(message.chat.id, f'⚡️ *Рассылка началась!*', parse_mode='Markdown')
                for user in users:
                    user = user[0]
                    try:
                        bot.send_message(user, f'{text}', parse_mode='Markdown', reply_markup=channel_markup)
                        x=x+1
                    except:
                        y=y+1
                bot.send_message(message.chat.id, f'⚡️ *Рассылка окончена!*\n\n*Пользователи:* {x}\n*Заблокировали бота:* {y}', parse_mode='Markdown', reply_markup=back_markup)
                connect.close()
            except:
                bot.send_message(f'{ID}', f'⚡️ *Ошибка!*', parse_mode="Markdown", reply_markup=back_markup)
                connect.close()

        bot.polling(none_stop=True)
    except:
        time.sleep(3)