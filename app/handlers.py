from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
import aiosqlite
import aiohttp
import time
import json

router = Router()
base_url = 'https://v6.exchangerate-api.com/v6/fcb0ea833aa4202bdb468701/latest'

@router.message(F.successful_payment)
async def makeUserSubscribe(message : Message):
    async with aiosqlite.connect("exchange_rate.db") as db:
        db.row_factory = aiosqlite.Row
        await db.execute("UPDATE user_data SET subscription = 1 WHERE user_id = ?", (message.from_user.id, ))
        await db.commit()
        

async def init_db():
    async with aiosqlite.connect("exchange_rate.db") as db:
        async with db.execute("""CREATE TABLE IF NOT EXISTS exchange_rates (
    base TEXT PRIMARY KEY,
    rates_json TEXT,
    updated_at INTEGER
)"""):
            
            await db.commit()
        async with db.execute("""CREATE TABLE IF NOT EXISTS user_data (
        user_id INTEGER,
        subscription BOOL
        )"""):
            await db.commit()


async def getValute(name, message : Message):
    async with aiosqlite.connect("exchange_rate.db") as db:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/{name}") as response:
                if response.status == 200:
                    api_data = await response.json()
                    rates_dict = api_data['conversion_rates']
                    updated_at = api_data['time_last_update_unix']
    
                    await db.execute("""INSERT OR REPLACE INTO exchange_rates (base, rates_json, updated_at) 
                        VALUES (?, ?, ?)""", (name, json.dumps(rates_dict), updated_at))
                    await db.commit()
                    return rates_dict
                else:
                    await message.answer("Ошибка при запросе к API.")
                    return

async def getDataAndSub(message : Message, valute):
    async with aiosqlite.connect("exchange_rate.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT rates_json, updated_at FROM exchange_rates WHERE base = ?", (valute,)) as c:
            row = await c.fetchone()
        async with db.execute("SELECT subscription FROM user_data WHERE user_id = ?", (message.from_user.id, )) as c:
            users = await c.fetchone()

        current_time = int(time.time())

        if users is None:
            await db.execute("INSERT INTO user_data (user_id, subscription) VALUES (?, ?)", (message.from_user.id, False))
            await db.commit()
            sub_status = False
        else:
            sub_status = users['subscription']

        if row and (current_time - row['updated_at'] < 3600):
            data = json.loads(row['rates_json'])
        else:
            data = await getValute(valute, message)

        return data, sub_status

@router.message(CommandStart())
async def cmd_start(message : Message):
    async with aiosqlite.connect("exchange_rate.db") as db:
        await db.execute("""INSERT OR IGNORE INTO user_data (user_id, subscription) 
                           VALUES (?, ?)""", (message.from_user.id, False))
        await db.commit()
    await message.answer("Привет! Я бот для перевода курса валют!", reply_markup=kb.MainKeyboard)

@router.message(F.text == "💲Получить курс доллара!")
async def getUSD(message : Message):

        data, sub_status = await getDataAndSub(message, "USD")

        if not data: return
        usd_to_rub = data.get("RUB")
        usd_to_eur = data.get("EUR")
        usd_to_kzt = data.get("KZT")
        usd_to_jpy = data.get("JPY")
        usd_to_cny = data.get("CNY")

        if sub_status == False:
            await message.answer(f"Курс💲1 USD (без подписки🙁): \n🪙{usd_to_rub:.2f} RUB\n💶{usd_to_eur:.2f} EUR\n ₸{usd_to_kzt:.2f} KZT")
        else:
            await message.answer(f"Курс💲1 USD (с подпиской🫰): \n🪙{usd_to_rub:.2f} RUB\n💶{usd_to_eur:.2f} EUR\n ₸{usd_to_kzt:.2f} KZT\n💴{usd_to_jpy:.2f} JPY\n💷{usd_to_cny:.2f} CNY")

@router.message(F.text == "🪙Получить курс рубля!")
async def getRUB(message : Message):
        data, sub_status = await getDataAndSub(message, "RUB")

        if not data: return
        rub_to_usd = data.get("USD") * 100
        rub_to_eur = data.get("EUR") * 100
        rub_to_kzt = data.get("KZT") * 100
        rub_to_jpy = data.get("JPY") * 100
        rub_to_cny = data.get("CNY") * 100
        if sub_status == False:
            await message.answer(f"Курс 🪙100 RUB (без подписки🙁): \n💲{rub_to_usd:.2f} USD\n💶{rub_to_eur:.2f} EUR\n ₸{rub_to_kzt:.2f} KZT")
        else:
            await message.answer(f"Курс 🪙100 RUB (c подпиской🫰): \n💲{rub_to_usd:.2f} USD\n💶{rub_to_eur:.2f} EUR\n ₸{rub_to_kzt:.2f} KZT\n💴{rub_to_jpy:.2f} JPY\n💷{rub_to_cny:.2f} CNY")

@router.message(F.text == "₸Получить курс тенге!")
async def getKZT(message : Message):
        data, sub_status = await getDataAndSub(message, "KZT")

        if not data: return
        kzt_to_usd = data.get("USD") * 1000
        kzt_to_rub = data.get("RUB") * 1000
        kzt_to_eur = data.get("EUR") * 1000
        kzt_to_jpy = data.get("JPY") * 1000
        kzt_to_cny = data.get("CNY") * 1000
        if sub_status == False:
            await message.answer(f"Курс ₸1000 KZT (без подписки🙁): \n💲{kzt_to_usd:.2f} USD\n🪙{kzt_to_rub:.2f} RUB\n💶{kzt_to_eur:.2f} EUR")
        else:
            await message.answer(f"Курс ₸1000 KZT (с подпиской🫰): \n💲{kzt_to_usd:.2f} USD\n🪙{kzt_to_rub:.2f} RUB\n💶{kzt_to_eur:.2f} EUR\n💴{kzt_to_jpy:.2f} JPY\n💷{kzt_to_cny:.2f} CNY")

@router.message(F.text == "💶Получить курс евро!")
async def getEUR(message : Message):
        data, sub_status = await getDataAndSub(message, "EUR")

        if not data: return
        eur_to_usd = data.get("USD")
        eur_to_rub = data.get("RUB")
        eur_to_kzt = data.get("KZT")
        eur_to_jpy = data.get("JPY")
        eur_to_cny = data.get("CNY")
        if sub_status == False:
            await message.answer(f"Курс 💶1 EUR (без подписки🙁): \n💲{eur_to_usd:.2f} USD\n🪙{eur_to_rub:.2f} RUB\n ₸{eur_to_kzt:.2f} KZT")
        else:
            await message.answer(f"Курс 💶1 EUR (с подпиской🫰): \n💲{eur_to_usd:.2f} USD\n🪙{eur_to_rub:.2f} RUB\n ₸{eur_to_kzt:.2f} KZT\n💴{eur_to_jpy:.2f} JPY\n💷{eur_to_cny:.2f} CNY") 

@router.message(F.text == "🛠️Подписка")
async def getStatusSubscribe(message : Message):
    async with aiosqlite.connect("exchange_rate.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT subscription FROM user_data WHERE user_id = ?", (message.from_user.id, )) as c:
            user = await c.fetchone()

        if user is None:
            await db.execute("INSERT INTO user_data (user_id, subscription) VALUES (?, ?)", (message.from_user.id, False))
            await db.commit()
            subscribe = False
        else:
            subscribe = user['subscription']

        if subscribe:
            await message.answer(f"Ваш статус подписки: ✅Подписка есть!")
        else:
            await message.answer("Ваш статус подписки: ❌Подписки нет!", reply_markup=kb.subscribeKeyboard)

@router.callback_query(F.data == "buySubscribe")
async def buySubscribe(callback : CallbackQuery):
    await callback.bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="💎Premium подписка",
        description="Доп доступ к валюте 💴Китая и 💷Японии!",
        payload="premium_sub",
        provider_token='',
        currency="XTR",
        prices=[{"label" : "Premium", "amount" : 99}]
    )


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: CallbackQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
