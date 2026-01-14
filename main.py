from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime, asyncio, logging
import openai

logging.basicConfig(level=logging.INFO)

# ------------------- CONFIG -------------------
BOT_TOKEN = "8229909104:AAFBB39RL5E3K9Qq7fwCy40wH4irBOkwuKc"          # Serverda qo‘yiladi
ADMIN_ID = 7968827951                      # Buyurtmalar keladigan admin ID
GROUP_URL = "https://t.me/+WyvBKxNmej5hMTg6"

# OpenAI API key
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Subscriberlar ro'yxati
subscribers = set()

# Toshkent rayonlari (lat/lon asosida)
RAYON = {
    "CHILONZOR": (41.25, 41.28, 69.15, 69.22),
    "OLMAZOR": (41.28, 41.31, 69.15, 69.22),
    "SHAYXONTOHUR": (41.31, 41.34, 69.15, 69.22),
    "YUNUSOBOD": (41.36, 41.39, 69.22, 69.28),
    "MIRZO_ULUGBEK": (41.30, 41.35, 69.28, 69.33),
    "SEBZOR": (41.32, 41.35, 69.33, 69.36),
    "QORASUV": (41.28, 41.31, 69.28, 69.33)
}

orders = {}

# --------- Keyboards ----------
def main_menu():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton("🍽 Bugungi menyu")],
        [KeyboardButton("📦 Buyurtma berish")]
    ])

def time_menu():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton("11:00–12:00"), KeyboardButton("12:00–13:00")],
        [KeyboardButton("13:00–14:00")]
    ])

def location_menu():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton("📍 Joylashuvingizni yuborish", request_location=True)]
    ])

def payment_menu():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton("Click / Karta"), KeyboardButton("Naqd")]
    ])

# --------- Helpers ----------
def get_rayon(lat, lon):
    for name, (lat_min, lat_max, lon_min, lon_max) in RAYON.items():
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return name
    return "NOMA’LUM"

async def chatgpt_response(question):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Mijoz savoliga javob ber: {question}",
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return "Kechirasiz, hozir javob bera olmayman."

async def send_feedback_request(user_id, order):
    await asyncio.sleep(3*3600)  # 3 soat
    try:
        await bot.send_message(user_id, "✅ Iltimos, buyurtma bo‘yicha taklif va etirozingizni yozing:")
    except Exception as e:
        print(f"Feedback xatolik: {e}")

async def send_to_group(order):
    text = (
        f"📦 Buyurtma:\n"
        f"👤 {order['name']}\n"
        f"📞 {order['phone']}\n"
        f"🍽 Ovqat: {order['food']} x {order['quantity']}\n"
        f"📍 Rayon: {order['rayon']}\n"
        f"💰 To‘lov: {order['payment']}\n"
        f"🗺 Xarita: {order['location']}"
    )
    try:
        await bot.send_message(chat_id=GROUP_URL, text=text)
    except Exception as e:
        print(f"Guruhga yuborishda xatolik: {e}")

# --------- Handlers ----------
@dp.message_handler(commands="start")
async def start(msg: types.Message):
    subscribers.add(msg.from_user.id)
    await msg.answer("👋 Colibri Catering botiga xush kelibsiz!", reply_markup=main_menu())

@dp.message_handler(text="🍽 Bugungi menyu")
async def menu(msg: types.Message):
    subscribers.add(msg.from_user.id)
    await msg.answer(
        "🍜 Qovurma lag‘mon — 30 000 so‘m\n"
        "🥩 Kotlet + pyure — 32 000 so‘m\n\n"
        "📦 Buyurtma berish tugmasini bosing"
    )

@dp.message_handler(text="📦 Buyurtma berish")
async def order_start(msg: types.Message):
    subscribers.add(msg.from_user.id)
    orders[msg.from_user.id] = {"name": msg.from_user.full_name}
    await msg.answer("⏰ Yetkazish vaqtini tanlang:", reply_markup=time_menu())

@dp.message_handler(lambda m: m.text in ["11:00–12:00", "12:00–13:00", "13:00–14:00"])
async def time_selected(msg: types.Message):
    orders[msg.from_user.id]["time"] = msg.text
    await msg.answer("📍 Joylashuvingizni yuboring:", reply_markup=location_menu())

@dp.message_handler(content_types=types.ContentType.LOCATION)
async def location_received(msg: types.Message):
    lat = msg.location.latitude
    lon = msg.location.longitude
    rayon = get_rayon(lat, lon)
    orders[msg.from_user.id]["location"] = f"https://maps.google.com/?q={lat},{lon}"
    orders[msg.from_user.id]["rayon"] = rayon
    await msg.answer("📞 Telefon raqamingizni yuboring:")

@dp.message_handler(lambda m: m.text and m.text.replace("+","").isdigit())
async def phone_received(msg: types.Message):
    orders[msg.from_user.id]["phone"] = msg.text
    await msg.answer("🍽 Ovqat turi va sonini kiriting (mas: Kotlet x 2):")

@dp.message_handler(lambda m: m.text and "x" in m.text)
async def food_received(msg: types.Message):
    orders[msg.from_user.id]["food"] = msg.text.split(" x ")[0]
    orders[msg.from_user.id]["quantity"] = msg.text.split(" x ")[1]
    await msg.answer("💡 Qo‘shimcha taklif yoki izoh yozing (majburiy emas):")
    
@dp.message_handler()
async def extras(msg: types.Message):
    orders[msg.from_user.id]["extras"] = msg.text
    await msg.answer("💰 To‘lov turini tanlang:", reply_markup=payment_menu())

@dp.message_handler(lambda m: m.text in ["Click / Karta", "Naqd"])
async def payment_received(msg: types.Message):
    orders[msg.from_user.id]["payment"] = msg.text
    if msg.text == "Click / Karta":
        await msg.answer("💳 Iltimos, to‘lovni ushbu karta orqali amalga oshiring:\n8600 0609 2138 2637 FN")
    else:
        await msg.answer("💵 To‘lov naqd qilib qabul qilindi.")
    
    await bot.send_message(ADMIN_ID, f"📦 YANGI BUYURTMA:\n{orders[msg.from_user.id]}")
    
    asyncio.create_task(asyncio.sleep(120))
    asyncio.create_task(send_to_group(orders[msg.from_user.id]))
    
    asyncio.create_task(send_feedback_request(msg.from_user.id, orders[msg.from_user.id]))
    
    await msg.answer("✅ Buyurtma qabul qilindi! Tez orada siz bilan bog‘lanamiz 😊")

# --------- Scheduler: 9:00AM Dushanba–Juma ---------
scheduler = AsyncIOScheduler()

async def send_daily_menu():
    today = datetime.datetime.today().weekday()
    if today < 5:
        for user_id in subscribers:
            try:
                await bot.send_message(
                    user_id,
                    "🍽 Bugungi menyu:\n🍜 Qovurma lag‘mon — 30 000 so‘m\n🥩 Kotlet + pyure — 32 000 so‘m\n\n📦 Buyurtma berish uchun botga xabar bering."
                )
            except Exception as e:
                print(f"Xatolik {user_id}: {e}")
    else:
        print("Bugun dam olish kuni, xabar yuborilmadi.")

async def on_startup(_):
    scheduler.add_job(send_daily_menu, 'cron', hour=9, minute=0)
    scheduler.start()

# --------- Start bot ----------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

