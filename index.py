import telebot
import requests
import json
import time
import threading
import os
import sys
import random
import string
from datetime import datetime, date
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from dotenv import load_dotenv
from keep_alive import keep_alive

# ================= KONFIGURASI =================
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    sys.exit("❌ ERROR: Token tidak ditemukan di .env")

# --- SETTING BATASAN ---
MAX_EMAILS_PER_DAY = 3      # Kuota harian
COOLDOWN_SECONDS = 60       # Jeda antar generate
REDEEM_ADD_QUOTA = 5        # Hadiah kuota
SESSION_DURATION = 300      # 5 MENIT (300 Detik) Max durasi email hidup

# --- BRANDING ---
WEBSITE_URL = "https://linktr.ee/Visualcodepo"
TIKTOK_URL = "https://www.tiktok.com/@raihan_official0307"
CREATOR_NAME = "Raihan_official0307 X Visualcodepo"

# --- FILE DB ---
DB_FILE = "users_db.json"
CODES_FILE = "codes.json"
API_URL = "https://api.mail.tm"

bot = telebot.TeleBot(TOKEN)

# ================= GLOBAL STATE (ANTRIAN) =================
# Variabel di RAM untuk mengatur antrian & sesi
active_sessions = {}   # Format: {chat_id: {data_email, start_time}}
waiting_queue = []     # List antrian: [chat_id_1, chat_id_2, ...]

# ================= DATABASE SYSTEM =================

def load_db():
    if not os.path.exists(DB_FILE): return {}
    with open(DB_FILE, 'r') as f: return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

def load_codes():
    if not os.path.exists(CODES_FILE):
        sample_codes = {"RAIHAN_GANTENG": True, "VISUALCODEPO": True}
        with open(CODES_FILE, 'w') as f: json.dump(sample_codes, f, indent=4)
        return sample_codes
    with open(CODES_FILE, 'r') as f: return json.load(f)

def save_codes(data):
    with open(CODES_FILE, 'w') as f: json.dump(data, f, indent=4)

# ================= LOGIC LIMIT =================

def check_user_limit(user_id):
    db = load_db()
    user_id = str(user_id)
    today_str = str(date.today())

    if user_id not in db:
        db[user_id] = {"quota": MAX_EMAILS_PER_DAY, "last_date": today_str, "last_gen_time": 0}
    
    user = db[user_id]

    # Reset Harian
    if user["last_date"] != today_str:
        user["quota"] = MAX_EMAILS_PER_DAY
        user["last_date"] = today_str
    
    if user["quota"] <= 0:
        return False, "⛔ **Limit Habis!**\nRedeem kode VIP atau kembali besok."

    save_db(db)
    return True, "OK"

def reduce_quota(user_id):
    db = load_db()
    user_id = str(user_id)
    if user_id in db:
        db[user_id]["quota"] -= 1
        db[user_id]["last_gen_time"] = time.time()
        save_db(db)

def add_quota(user_id, amount):
    db = load_db()
    user_id = str(user_id)
    if user_id in db:
        db[user_id]["quota"] += amount
        save_db(db)

# ================= LOGIC ANTRIAN (QUEUE) =================

def process_next_in_queue():
    """Memanggil user berikutnya dalam antrian"""
    global waiting_queue
    
    if len(waiting_queue) > 0:
        next_user_id = waiting_queue.pop(0) # Ambil user pertama
        
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("✅ Lanjutkan (Buat Email)", callback_data="queue_accept"))
        markup.row(InlineKeyboardButton("❌ Batalkan", callback_data="queue_deny"))
        
        try:
            bot.send_message(
                next_user_id,
                "🔔 **GILIRAN ANDA TIBA!**\n\n"
                "User sebelumnya telah selesai.\n"
                "Silakan pilih tindakan di bawah ini:",
                reply_markup=markup
            )
        except Exception as e:
            # Jika user memblokir bot, skip ke user berikutnya
            process_next_in_queue()

# ================= API WRAPPER =================

def create_account_api():
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    try:
        domain_resp = requests.get(f"{API_URL}/domains").json()
        domain = domain_resp['hydra:member'][0]['domain']
    except:
        domain = "vemail.net" # Fallback

    username = ''.join(random.choices(string.ascii_lowercase, k=8))
    email = f"{username}@{domain}"

    reg = requests.post(f"{API_URL}/accounts", json={"address": email, "password": password})
    if reg.status_code != 201: raise Exception("Gagal Register API")
    
    tok = requests.post(f"{API_URL}/token", json={"address": email, "password": password})
    token = tok.json()['token']
    
    return {"email": email, "password": password, "token": token, "id": reg.json()['id'], "last_msg_id": None}

# ================= BACKGROUND WORKER (AUTO-NOTIF & TIMEOUT) =================

def background_worker():
    print("⚙️ Worker Berjalan (Inbox Check & Queue Timeout)...")
    while True:
        try:
            current_time = time.time()
            # Copy untuk iterasi aman
            sessions_copy = list(active_sessions.items())
            
            for chat_id, session in sessions_copy:
                # 1. CEK DURASI (5 MENIT LIMIT)
                elapsed = current_time - session['start_time']
                if elapsed > SESSION_DURATION:
                    # Force Stop
                    try:
                        bot.send_message(chat_id, "⏱ **WAKTU HABIS (5 Menit)!**\nSesi Anda dihentikan otomatis untuk memberi giliran ke antrian.")
                    except: pass
                    
                    # Hapus sesi & Panggil antrian
                    del active_sessions[chat_id]
                    process_next_in_queue()
                    continue # Skip cek inbox krn user dah dikick

                # 2. CEK INBOX
                try:
                    headers = {"Authorization": f"Bearer {session['token']}"}
                    resp = requests.get(f"{API_URL}/messages?page=1", headers=headers)
                    if resp.status_code == 200:
                        msgs = resp.json()['hydra:member']
                        if msgs:
                            latest = msgs[0]
                            if latest['id'] != session.get('last_msg_id'):
                                active_sessions[chat_id]['last_msg_id'] = latest['id']
                                
                                sender = latest['from']['name'] or latest['from']['address']
                                sub = latest['subject'] or "(No Subject)"
                                
                                text = f"🔔 **EMAIL MASUK!**\n📨 **Dari:** {sender}\n🏷 **Subjek:** {sub}"
                                markup = InlineKeyboardMarkup()
                                markup.add(InlineKeyboardButton("📖 BACA", callback_data=f"read|{latest['id']}"))
                                bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=markup)
                except: continue
            
            time.sleep(5) # Cek setiap 5 detik
        except Exception as e:
            print(f"Worker Error: {e}")
            time.sleep(5)

t = threading.Thread(target=background_worker)
t.daemon = True
t.start()

# ================= BOT HANDLER =================

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    check_user_limit(user_id)
    db = load_db()
    quota = db[user_id]['quota']
    
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🔥 Buat Email", callback_data="gen"))
    markup.row(InlineKeyboardButton("👤 Profil", callback_data="profile"),
               InlineKeyboardButton("💎 Redeem", callback_data="redeem"))
    markup.row(InlineKeyboardButton("🌐 Admin Web", url=WEBSITE_URL))
    markup.row(InlineKeyboardButton("👨‍💻 Creator Info", callback_data="creator"))

    text = (
        f"🔰 **MAIL SYSTEM V6 (Queue)**\n"
        f"Hai, {message.from_user.first_name}!\n\n"
        f"⚠️ **ATURAN PENTING:**\n"
        f"1. **Sistem Antrian:** Hanya 1 user yang bisa buat email dalam satu waktu.\n"
        f"2. **Durasi:** Email hanya aktif **5 Menit**, lalu otomatis terhapus.\n"
        f"3. **Kuota:** `{quota}` Email/Hari.\n\n"
        f"👇 Klik tombol untuk memulai."
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    
    try:
        # --- GENERATE REQUEST ---
        if call.data == "gen":
            # 1. Cek Limit User
            allowed, msg = check_user_limit(chat_id)
            if not allowed:
                bot.answer_callback_query(call.id, "Limit Habis!", show_alert=True)
                return

            # 2. CEK APAKAH ADA SESI AKTIF (SISTEM ANTRIAN)
            if len(active_sessions) > 0:
                # Cek apakah user ini yang sedang aktif?
                if chat_id in active_sessions:
                    bot.answer_callback_query(call.id, "Anda sedang dalam sesi aktif!", show_alert=True)
                else:
                    # Masukkan ke Antrian
                    if chat_id not in waiting_queue:
                        waiting_queue.append(chat_id)
                    
                    posisi = waiting_queue.index(chat_id) + 1
                    bot.send_message(chat_id, f"⏳ **ANTRIAN PENUH**\n\nAda user lain yang sedang membuat email.\nAnda masuk antrian nomor: **{posisi}**\n\nMohon tunggu, bot akan memberi tahu saat giliran Anda tiba.")
            else:
                # Kosong -> Langsung Buat
                start_email_session(chat_id, call.message)

        # --- USER MENERIMA GILIRAN DARI ANTRIAN ---
        elif call.data == "queue_accept":
            # Hapus pesan konfirmasi
            bot.delete_message(chat_id, call.message.message_id)
            # Cek lagi limit biar aman
            allowed, _ = check_user_limit(chat_id)
            if allowed:
                start_email_session(chat_id, call.message)
            else:
                bot.send_message(chat_id, "Limit Anda habis saat menunggu.")
                process_next_in_queue()

        # --- USER MENOLAK GILIRAN ---
        elif call.data == "queue_deny":
            bot.delete_message(chat_id, call.message.message_id)
            bot.send_message(chat_id, "❌ Anda membatalkan antrian.")
            process_next_in_queue() # Panggil user selanjutnya

        # --- STOP / SELESAI ---
        elif call.data == "stop":
            if chat_id in active_sessions:
                del active_sessions[chat_id]
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("🏠 Menu", callback_data="menu"))
                bot.edit_message_text("🛑 **Sesi Dihentikan.**", chat_id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')
                
                # TRIGGER ANTRIAN SELANJUTNYA
                process_next_in_queue()

        # --- READ EMAIL ---
        elif call.data.startswith("read|"):
            if chat_id not in active_sessions:
                bot.answer_callback_query(call.id, "Sesi habis/Antrian lewat.", show_alert=True)
                return
            msg_id = call.data.split("|")[1]
            token = active_sessions[chat_id]['token']
            m = requests.get(f"{API_URL}/messages/{msg_id}", headers={"Authorization": f"Bearer {token}"}).json()
            body = m.get('text') or "HTML Content"
            if len(body)>3000: body=body[:3000]+"..."
            bot.send_message(chat_id, f"📨 **PESAN:**\n\n{body}")

        # --- MENU LAINNYA ---
        elif call.data == "creator":
            text = f"👨‍💻 **CREATOR**\n\n👑 {CREATOR_NAME}\n📱 TikTok: {TIKTOK_URL}\n🌐 Web: {WEBSITE_URL}"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🎵 TikTok", url=TIKTOK_URL), InlineKeyboardButton("🔙", callback_data="menu"))
            bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)

        elif call.data == "profile":
            db = load_db()
            d = db.get(str(chat_id), {"quota":0})
            text = f"👤 **Profil**\nID: `{chat_id}`\nSisa Kuota: {d['quota']}"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙", callback_data="menu"))
            bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')

        elif call.data == "menu":
            start(call.message)
            
        elif call.data == "redeem":
            msg = bot.send_message(chat_id, "Kirim KODE REDEEM:", reply_markup=ForceReply())
            bot.register_next_step_handler(msg, process_redeem)

    except Exception as e:
        print(f"Err: {e}")

def start_email_session(chat_id, message_obj):
    """Fungsi core untuk memulai sesi email"""
    bot.send_message(chat_id, "⚙️ Sedang membuat akun (Mohon tunggu)...")
    try:
        session = create_account_api()
        session['start_time'] = time.time() # Catat waktu mulai
        active_sessions[chat_id] = session
        reduce_quota(chat_id)
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🛑 Stop & Ganti Giliran", callback_data="stop"))
        
        text = (
            "✅ **EMAIL AKTIF (5 Menit)**\n"
            "➖➖➖➖➖➖➖➖➖➖\n"
            f"📧 `{session['email']}`\n\n"
            "⚡ **Mohon segera gunakan!**\n"
            "Jika sudah selesai, TEKAN TOMBOL STOP agar user lain bisa pakai.\n"
            "_(Otomatis mati dalam 5 menit)_"
        )
        bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=markup)
    except Exception as e:
        bot.send_message(chat_id, f"Error: {e}")
        process_next_in_queue() # Jika error, lempar ke antrian berikutnya

def process_redeem(message):
    code = message.text.strip()
    codes = load_codes()
    if code in codes and codes[code]:
        codes[code] = False
        save_codes(codes)
        add_quota(message.chat.id, REDEEM_ADD_QUOTA)
        bot.reply_to(message, f"✅ Kuota +{REDEEM_ADD_QUOTA} Berhasil!")
    else:
        bot.reply_to(message, "❌ Kode Salah.")

# ================= RUN =================
if __name__ == "__main__":
    print("🚀 Bot V6 (Queue System) Running...")
    keep_alive()
    try: bot.infinity_polling()
    except: pass