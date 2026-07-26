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
    rates_json REAL,
    updated_at INTEGER,
    PRIMARY KEY (base, target)
)"""):
            await db.commit()


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
            print(data['RUB'])
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url}/USD") as response:
                    if response.status == 200:
                        api_data = await response.json()
                        rates_dict = api_data['conversion_rates']
                        updated_at = api_data['time_last_update_unix']

                        await db.execute("""INSERT OR REPLACE INTO exchange_rates (base, rates_json, updated_at) 
                            VALUES (?, ?, ?)""", ("USD", json.dumps(rates_dict), updated_at))
                        await db.commit()
                        data = rates_dict
                    else:
                        await message.answer("Ошибка при запросе к API.")
                        return

        usd_to_rub = data.get("RUB")
        usd_to_eur = data.get("EUR")
        usd_to_kzt = data.get("KZT")
        await message.answer(f"Курс 1 USD: \n{usd_to_rub} RUB\n{usd_to_eur} EUR\n{usd_to_kzt} KZT")