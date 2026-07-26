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

async def init_db():
    async with aiosqlite.connect("exchange_rate.db") as db:
        async with db.execute("""CREATE TABLE IF NOT EXISTS exchange_rates (
    base TEXT,
    target TEXT,
    rates_json TEXT,
    updated_at INTEGER,
    PRIMARY KEY (base, target)
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

@router.message(CommandStart())
async def cmd_start(message : Message):
    await message.answer("Привет! Я бот для перевода курса валют!", reply_markup=kb.MainKeyboard)

@router.message(F.text == "💲Получить курс доллара!")
async def getUSD(message : Message):
    async with aiosqlite.connect("exchange_rate.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT rates_json, updated_at FROM exchange_rates WHERE base = ?", ("USD",)) as c:
            row = await c.fetchone()

        current_time = int(time.time())

        if row and (current_time - row['updated_at'] < 3600):
            data = json.loads(row['rates_json'])
        else:
            data = await getValute("USD", message)
            
        if not data: return
        usd_to_rub = data.get("RUB")
        usd_to_eur = data.get("EUR")
        usd_to_kzt = data.get("KZT")
        await message.answer(f"Курс💲1 USD: \n🪙{usd_to_rub:.2f} RUB\n💶{usd_to_eur:.2f} EUR\n ₸{usd_to_kzt:.2f} KZT")

@router.message(F.text == "🪙Получить курс рубля!")
async def getRUB(message : Message):
    async with aiosqlite.connect("exchange_rate.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT rates_json, updated_at FROM exchange_rates WHERE base = ?", ("RUB", )) as c:
            row = await c.fetchone()

        current_time = int(time.time())

        if row and (current_time - row['updated_at'] < 3600):
            data = json.loads(row['rates_json'])
        else:
            data = await getValute("RUB", message)

        if not data: return
        rub_to_usd = data.get("USD") * 100
        rub_to_eur = data.get("EUR") * 100
        rub_to_kzt = data.get("KZT") * 100
        await message.answer(f"Курс 🪙100 RUB: \n💲{rub_to_usd:.2f} USD\n💶{rub_to_eur:.2f} EUR\n ₸{rub_to_kzt:.2f} KZT")

@router.message(F.text == "₸Получить курс тенге!")
async def getKZT(message : Message):
    async with aiosqlite.connect("exchange_rate.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT rates_json, updated_at FROM exchange_rates WHERE base = ?", ("KZT", )) as c:
            row = await c.fetchone()

        current_time = int(time.time())

        if row and (current_time - row['updated_at'] < 3600):
            data = json.loads(row['rates_json'])
        else:
            data = await getValute("KZT", message)

        if not data: return
        kzt_to_usd = data.get("USD") * 1000
        kzt_to_rub = data.get("RUB") * 1000
        kzt_to_eur = data.get("EUR") * 1000
        await message.answer(f"Курс ₸1000 KZT: \n💲{kzt_to_usd:.2f} USD\n🪙{kzt_to_rub:.2f} RUB\n💶{kzt_to_eur:.2f} EUR")

@router.message(F.text == "💶Получить курс евро!")
async def getEUR(message : Message):
    async with aiosqlite.connect("exchange_rate.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT rates_json, updated_at FROM exchange_rates WHERE base = ?", ("EUR", )) as c:
            row = await c.fetchone()

        current_time = int(time.time())

        if row and (current_time - row['updated_at'] < 3600):
            data = json.loads(row['rates_json'])
        else:
            data = await getValute("EUR", message)

        if not data: return
        eur_to_usd = data.get("USD")
        eur_to_rub = data.get("RUB")
        eur_to_kzt = data.get("KZT")
        await message.answer(f"Курс 💶1 EUR: \n💲{eur_to_usd:.2f} USD\n🪙{eur_to_rub:.2f} RUB\n ₸{eur_to_kzt:.2f} KZT")