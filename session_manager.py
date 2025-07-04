from telethon import TelegramClient
import os
import asyncio

if not os.path.exists('sessions'):
    os.makedirs('sessions')

async def create_session(api_id, api_hash, phone_number):
    session_name = f'sessions/{phone_number}'
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        code = input("Код: ")
        try:
            await client.sign_in(phone_number, code)
        except:
            password = input("Пароль (2FA): ")
            await client.sign_in(password=password)
    print(f"Сессия готова: {session_name}.session")
    await client.disconnect()

async def main():
    api_id = 20401021
    api_hash = '7fa6c7f62816334c230cebf77c565c3d'
    phone_number = input("Номер: ")
    await create_session(api_id, api_hash, phone_number)

if __name__ == '__main__':
    asyncio.run(main())
