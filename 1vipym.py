from flask import Flask, request, jsonify, render_template_string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import requests, re, asyncio, threading
import os

# === CẤU HÌNH ===
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8029254946:AAE8Upy5LoYIYsmcm8Y117Esm_-_MF0-ChA')
app = Flask(__name__)

# === DANH SÁCH NHIỆM VỤ/NÚT BYPASS & HƯỚNG DẪN ===
TASKS = [
    {"label": "Bypass M88", "type": "m88"},
    {"label": "Bypass FB88", "type": "fb88"},
    {"label": "Bypass 188BET", "type": "188bet"},
    {"label": "Bypass W88", "type": "w88"},
    {"label": "Bypass V9BET", "type": "v9bet"},
    {"label": "Bypass BK8", "type": "bk8"},
]
HELP_BUTTON = {"label": "📖 Hướng dẫn / Hỗ trợ", "callback": "help"}

# === TEMPLATE HTML ĐẸP CHO TRANG BỎ QUA ===
BYPASS_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>BYPASS TRAFFIC | YM5 Tool</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            background: linear-gradient(135deg, #232526, #414345); 
            color: #fff; 
            font-family: 'Segoe UI', sans-serif; 
            margin: 0; 
            padding: 0;
            min-height: 100vh;
            display: flex; 
            align-items: center; 
            justify-content: center;
            flex-direction: column;
        }
        .container {
            background: rgba(30, 30, 40, 0.98);
            padding: 32px 24px 24px 24px;
            border-radius: 20px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.4);
            max-width: 350px;
            width: 100%;
        }
        h1 {
            margin: 0 0 18px 0;
            font-size: 2.1rem;
            font-weight: 500;
            text-align: center;
            letter-spacing: 2px;
            color: #7cf6ff;
        }
        select, button {
            width: 100%;
            padding: 12px;
            margin-top: 14px;
            border: none;
            border-radius: 8px;
            font-size: 1.05rem;
        }
        select { background: #252836; color: #fff; }
        button {
            background: linear-gradient(90deg, #34e89e 0%, #0f3443 100%);
            color: #fff;
            font-weight: bold;
            cursor: pointer;
            margin-bottom: 10px;
        }
        #result {
            margin-top: 18px;
            padding: 18px;
            border-radius: 10px;
            background: rgba(40, 255, 230, 0.08);
            font-size: 1.07rem;
            min-height: 32px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,255,255,0.05);
        }
        .spinner {
            border: 3px solid #eee;
            border-top: 3px solid #04e8f9;
            border-radius: 50%;
            width: 30px; height: 30px;
            animation: spin 0.8s linear infinite;
            display: inline-block;
            margin-bottom: -8px;
        }
        @keyframes spin {
            0% { transform: rotate(0); }
            100% { transform: rotate(360deg);}
        }
        .footer {
            margin-top: 30px;
            color: #aaa;
            font-size: 0.99rem;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>BYPASS TRAFFIC</h1>
        <select id="type">
            <option value="m88">M88</option>
            <option value="fb88">FB88</option>
            <option value="188bet">188BET</option>
            <option value="w88">W88</option>
            <option value="v9bet">V9BET</option>
            <option value="bk8">BK8</option>
        </select>
        <button onclick="submitForm()">LẤY MÃ</button>
        <div id="result"></div>
    </div>
    <div class="footer">
        YM5 Tool &copy; 2025 &mdash; <a href="https://t.me/doanh444" target="_blank" style="color:#43e8d8;text-decoration:none;">Bóng X Nhóm Telegram</a>
    </div>
<script>
function submitForm() {
    var type = document.getElementById('type').value;
    var resultDiv = document.getElementById('result');
    resultDiv.innerHTML = '<div class="spinner"></div> <span style="font-size:1.06rem">Đang lấy mã... Vui lòng chờ 75 giây</span>';
    fetch('/bypass', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({type: type})
    })
    .then(res => res.json())
    .then(data => {
        resultDiv.innerHTML = formatResult(data.msg);
    })
    .catch(e => resultDiv.innerHTML = "<span style='color:#ff6f6f;'>Lỗi: Không thể kết nối máy chủ.</span>");
}

function formatResult(msg) {
    if(msg.includes('✅')) {
        return `<span style="color:#31ff8a;font-weight:bold;font-size:1.18rem;">${msg}</span>`;
    } else if(msg.includes('⚠️')) {
        return `<span style="color:#ffd166;">${msg}</span>`;
    } else if(msg.includes('❌')) {
        return `<span style="color:#ff6f6f;">${msg}</span>`;
    } else {
        return msg;
    }
}
</script>
</body>
</html>
"""

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
            return f'✅ <b>{name}</b> | <b style="color:#32e1b7;">Mã</b>: <code>{match.group(1)}</code>'
        else:
            return f'⚠️ <b>{name}</b> | <span style="color:#ffd166;">Không tìm thấy mã</span>'
    except Exception as e:
        return f'❌ <b>Lỗi khi lấy mã:</b> <code>{e}</code>'

# === GỬI MENU NHIỆM VỤ ===
async def send_main_menu(chat_id, context):
    keyboard = []
    for i in range(0, len(TASKS), 2):
        line = []
        for task in TASKS[i:i+2]:
            line.append(InlineKeyboardButton(task["label"], callback_data=f"bypass:{task['type']}"))
        keyboard.append(line)
    keyboard.append([InlineKeyboardButton(HELP_BUTTON["label"], callback_data=HELP_BUTTON["callback"])])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "<b>🔰 CHỌN NHIỆM VỤ BYPASS-BÓNG X:</b>\n"
            "Bạn có thể tiếp tục chọn nhiệm vụ khác hoặc xem hướng dẫn 👇"
        ),
        parse_mode="HTML",
        reply_markup=reply_markup
    )

# === XỬ LÝ NÚT NHIỆM VỤ, HƯỚNG DẪN VÀ HỖ TRỢ ===
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Xử lý các nút thao tác trong hướng dẫn
    if data == "mainmenu":
        await send_main_menu(query.message.chat_id, context)
        return

    if data == "contact_admin":
        await query.edit_message_text(
            "<b>💬 Liên hệ hỗ trợ:</b>\n"
            "Bạn có thể nhắn trực tiếp cho <b>@doanh21110</b> qua Telegram:\n"
            "<a href='https://t.me/doanh444'>@doanh444</a>\n"
            "\n"
            "Hoặc tham gia nhóm <b>Bóng X</b> để cùng trao đổi, hỗ trợ:\n"
            "<a href='https://t.me/doanh444'>https://t.me/doanh444</a>",
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Quay lại hướng dẫn", callback_data="help")],
                [InlineKeyboardButton("🏠 Quay lại Menu", callback_data="mainmenu")]
            ])
        )
        return

    # Nút Hướng dẫn/Hỗ trợ
    if data == HELP_BUTTON["callback"]:
        help_text = (
            "<b>📖 HƯỚNG DẪN SỬ DỤNG BOT BYPASS & HỖ TRỢ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>1. CÁC CHỨC NĂNG CHÍNH:</b>\n"
            "• Bypass traffic (lấy mã) cho các loại: <b>M88, FB88, 188BET, W88, V9BET, BK8</b>.\n"
            "• Giao diện Telegram cực dễ dùng, thao tác nhanh chóng.\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>2. CÁCH SỬ DỤNG:</b>\n"
            "<b>🔹 Cách 1: Dùng các NÚT NHIỆM VỤ</b>\n"
            "– Nhấn vào nút nhiệm vụ (Bypass M88, Bypass FB88, ...) trong menu chính.\n"
            "– Bot báo trạng thái đang xử lý và tự động gửi kết quả sau 75 giây.\n"
            "<b>🔹 Cách 2: Dùng lệnh thủ công</b>\n"
            "– Nhập lệnh: <code>/ym &lt;loại&gt;</code>\n"
            "– Ví dụ: <code>/ym m88</code> hoặc <code>/ym bk8</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>3. CÁC LOẠI HỖ TRỢ:</b>\n"
            "- <b>M88, FB88, 188BET, W88, V9BET, BK8</b>\n"
            "- Nếu nhập sai loại, bot sẽ báo lỗi.\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>4. LƯU Ý QUAN TRỌNG:</b>\n"
            "• Chỉ sử dụng các loại hợp lệ, không thử loại khác!\n"
            "• Không spam nhiều nhiệm vụ liên tục, hãy đợi kết quả trước khi làm tiếp.\n"
            "• Nếu mã không ra hoặc báo lỗi, thử lại sau vài phút hoặc liên hệ admin.\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>5. HỖ TRỢ & LIÊN HỆ:</b>\n"
            "• Nhấn nút bên dưới để liên hệ admin hoặc vào nhóm Telegram <b>Bóng X</b> cùng Doanh D3939 hỗ trợ.\n"
            "• Admin: <a href='https://t.me/doanh444'>@doanh444</a> | Nhóm: <a href='https://t.me/doanh444'>https://t.me/doanh444</a>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "<i>Chúc bạn thành công! 🚀</i>"
        )
        help_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Quay lại Menu", callback_data="mainmenu")],
            [InlineKeyboardButton("💬 Liên hệ Admin & Nhóm", callback_data="contact_admin")]
        ])
        await query.edit_message_text(
            help_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=help_keyboard
        )
        return

    # Xử lý nhiệm vụ bypass như cũ...
    if data.startswith("bypass:"):
        type = data.split(":", 1)[1]
        user = query.from_user.first_name or "User"
        await query.edit_message_text(
            f"⏳ <b>Đang thực hiện nhiệm vụ:</b> <code>{type}</code>\n"
            f"<i>Vui lòng chờ 75 giây để lấy kết quả...</i>",
            parse_mode="HTML"
        )

        async def delay_and_reply():
            await asyncio.sleep(75)
            result = bypass(type)
            if "✅" in result:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=(
                        "<b>🎉 KẾT QUẢ BYPASS</b>\n"
                        "<b>─────────────────────────────</b>\n"
                        f"{result}\n"
                        "<b>─────────────────────────────</b>\n"
                        "👉 <i>Chúc bạn thành công!</i>"
                    ),
                    parse_mode="HTML"
                )
            elif "⚠️" in result:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=(
                        "<b>⚠️ THÔNG BÁO</b>\n"
                        "<b>─────────────────────────────</b>\n"
                        f"{result}\n"
                        "<b>─────────────────────────────</b>\n"
                        "<i>Hãy kiểm tra lại loại bạn chọn!</i>"
                    ),
                    parse_mode="HTML"
                )
            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=(
                        "<b>❌ LỖI</b>\n"
                        "<b>─────────────────────────────</b>\n"
                        f"{result}\n"
                        "<b>─────────────────────────────</b>"
                    ),
                    parse_mode="HTML"
                )
            # Gợi ý menu nhiệm vụ tiếp theo
            await send_main_menu(query.message.chat_id, context)

        asyncio.create_task(delay_and_reply())

# === LỆNH /ym XỬ LÝ SONG SONG ===
async def ym_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_html(
            "📌 <b>Hướng dẫn sử dụng:</b>\n"
            "<b>/ym &lt;loại&gt;</b>\n"
            "Ví dụ: <code>/ym m88</code>\n"
            "<b>Các loại hợp lệ:</b> <i>m88, fb88, 188bet, w88, v9bet, bk8</i>"
        )
        return

    type = context.args[0].lower()
    user = update.effective_user.first_name or "User"
    await update.message.reply_html(
        f"🕒 <b>Xin chào {user}!</b>\n"
        "Đang xử lý, vui lòng đợi <b>75 giây</b> để lấy mã...\n"
        "<i>Bạn sẽ nhận được thông báo kết quả tự động.</i>"
    )

    async def delay_and_reply():
        await asyncio.sleep(75)
        result = bypass(type)
        if "✅" in result:
            await update.message.reply_html(
                "<b>🎉 KẾT QUẢ BYPASS</b>\n"
                "<b>─────────────────────────────</b>\n"
                f"{result}\n"
                "<b>─────────────────────────────</b>\n"
                "👉 <i>Chúc bạn thành công!</i>"
            )
        elif "⚠️" in result:
            await update.message.reply_html(
                "<b>⚠️ THÔNG BÁO</b>\n"
                "<b>─────────────────────────────</b>\n"
                f"{result}\n"
                "<b>─────────────────────────────</b>\n"
                "<i>Hãy kiểm tra lại loại bạn nhập!</i>"
            )
        else:
            await update.message.reply_html(
                "<b>❌ LỖI</b>\n"
                "<b>─────────────────────────────</b>\n"
                f"{result}\n"
                "<b>─────────────────────────────</b>"
            )
        await send_main_menu(update.effective_chat.id, context)

    asyncio.create_task(delay_and_reply())

# === API BỎ QUA TRAFFIC ===
@app.route('/bypass', methods=['POST'])
def handle_api():
    json_data = request.get_json()
    type = json_data.get('type')
    result = bypass(type)
    return jsonify({'msg': result})

@app.route('/', methods=['GET'])
def index():
    return render_template_string(BYPASS_TEMPLATE)

def start_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    threading.Thread(target=start_flask).start()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", lambda update, ctx: send_main_menu(update.effective_chat.id, ctx)))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CommandHandler("ym", ym_command))
    application.run_polling()