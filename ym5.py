from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests, re, asyncio, threading

# === CẤU HÌNH ===
BOT_TOKEN = '7376236700:AAErRQrxoCrnWpbF4zPfV0SzKU4JhjNG200'
CHAT_ID = '-1002723056627'
app = Flask(__name__)

# === HÀM BYPASS MÃ ===
def bypass(type):
    config = {
        'm88':   ('M88', 'https://bet88ec.com/cach-danh-bai-sam-loc', 'https://bet88ec.com/', 'taodeptrai'),
        'fb88':  ('FB88', 'https://fb88mg.com/ty-le-cuoc-hong-kong-la-gi', 'https://fb88mg.com/', 'taodeptrai'),
        '188bet':('188BET', 'https://88betag.com/cach-choi-game-bai-pok-deng', 'https://88betag.com/', 'taodeptrailamnhe'),
        'w88':   ('W88', 'https://188.166.185.213/tim-hieu-khai-niem-3-bet-trong-poker-la-gi', 'https://188.166.185.213/', 'taodeptrai'),
        'v9bet': ('V9BET', 'https://v9betse.com/ca-cuoc-dua-cho', 'https://v9betse.com/', 'taodeptrai'),
        'bk8':   ('BK8', 'https://bk8ze.com/cach-choi-bai-catte', 'https://bk8ze.com/', 'taodeptrai')
    }

    if type not in config:
        return f'❌ Sai loại: <code>{type}</code>'

    name, url, ref, code_key = config[type]
    try:
        res = requests.post(f'https://traffic-user.net/GET_MA.php?codexn={code_key}&url={url}&loai_traffic={ref}&clk=1000')
        match = re.search(r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>', res.text)
        if match:
            return f'✅ <b>{name}</b> | Mã: <code>{match.group(1)}</code>'
        else:
            return f'⚠️ {name} | Không tìm thấy mã'
    except Exception as e:
        return f'❌ Lỗi khi lấy mã: {e}'

# === LỆNH /ym XỬ LÝ SONG SONG ===
async def ym_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📌 Dùng đúng: /ym <type>", parse_mode="HTML")
        return

    type = context.args[0].lower()
    user = update.effective_user.first_name or "User"

    await update.message.reply_text("🕒 Đang xử lý... vui lòng đợi 75 giây", parse_mode="HTML")

    async def delay_and_reply():
        await asyncio.sleep(75)
        result = bypass(type)
        await update.message.reply_text(result, parse_mode="HTML")

    # Tạo task riêng biệt để không chặn người khác
    asyncio.create_task(delay_and_reply())

# === API BỎ QUA TRAFFIC ===
@app.route('/bypass', methods=['POST'])
def handle_api():
    json_data = request.get_json()
    type = json_data.get('type')
    result = bypass(type)
    return jsonify({'msg': result})

# === FLASK CHẠY NỀN SONG SONG ===
def start_flask():
    app.run(host="0.0.0.0", port=5000)

# === MAIN CHẠY CẢ HAI ===
if __name__ == "__main__":
    threading.Thread(target=start_flask).start()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("ym", ym_command))
    application.run_polling()