import requests
import time
from datetime import datetime, timedelta, timezone
from rich.console import Console
from rich.table import Table
from rich import box

TELEGRAM_TOKEN = "7785351537:AAHdxL61w6uRnJnRVkXrIFTfgH1I8fkoAhM"
CHAT_IDS = ["-1002723056627"]
ADMIN_ID = "6463176046"

# Chỉ sử dụng chiến lược streak
strategies = ["streak"]
strategy_stats = {s: {"correct": 0, "total": 0} for s in strategies}

last_sent_session_id = None
correct = 0
wrong = 0
last_prediction = None
last_prediction_session_id = None
is_bot_enabled = True
last_update_id = 0

console = Console()


def get_result(sum_dice):
    return "Tài" if sum_dice >= 11 else "Xỉu"


def get_vn_time():
    VN_TZ = timezone(timedelta(hours=7))
    now = datetime.now(VN_TZ)
    return now.strftime("%H:%M:%S - %d/%m/%Y")


def predict_by_strategy(data, strategy):
    if strategy == "streak":
        last_result = get_result(data[0]["FirstDice"] + data[0]["SecondDice"] + data[0]["ThirdDice"])
        streak_value = last_result
        streak_count = 1
        for i in range(1, len(data)):
            result = get_result(data[i]["FirstDice"] + data[i]["SecondDice"] + data[i]["ThirdDice"])
            if result == streak_value:
                streak_count += 1
            else:
                break
        if streak_count >= 3:
            return "Xỉu" if streak_value == "Tài" else "Tài"
        else:
            return streak_value
    else:
        return "Tài"  # Dự phòng, không dùng


def get_final_prediction(data):
    result = predict_by_strategy(data, "streak")
    return result, {"streak": result}


def fetch_data():
    try:
        res = requests.get("https://taixiu1.gsum01.com/api/luckydice1/GetSoiCau")
        return res.json()[:10]
    except Exception as e:
        console.print(f"[red]Lỗi lấy dữ liệu: {e}[/]")
        return []


def send_telegram_message(text):
    for chat_id in CHAT_IDS:
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            )
            if response.status_code != 200:
                console.print(f"[red]❌ Lỗi gửi Telegram: {response.text}[/]")
        except Exception as e:
            console.print(f"[red]Lỗi gửi Telegram: {e}[/]")


def check_telegram_command():
    global is_bot_enabled, last_update_id
    try:
        res = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={last_update_id + 1}"
        )
        data = res.json()
        updates = data.get("result", [])
        for update in updates:
            last_update_id = update["update_id"]
            msg = update.get("message", {})
            if str(msg.get("from", {}).get("id")) != ADMIN_ID:
                continue
            text = msg.get("text", "").lower()
            if text == "/on":
                is_bot_enabled = True
                send_telegram_message("✅ Bot đã *bật* gửi dự đoán.")
                console.print("[green]✅ Bot đã BẬT gửi dự đoán.[/]")
            elif text == "/off":
                is_bot_enabled = False
                send_telegram_message("⛔ Bot đã *tắt* gửi dự đoán.")
                console.print("[red]⛔ Bot đã TẮT gửi dự đoán.[/]")
    except Exception as e:
        console.print(f"[red]Lỗi kiểm tra lệnh: {e}[/]")


def display_to_console(session_id, current_result, final_prediction, individuals, accuracy):
    table = Table(title=f"[bold magenta]🎯 TOOL TÀI XỈU - Phiên {session_id}[/]", box=box.SQUARE)
    table.add_column("Chiến lược", style="cyan", justify="left")
    table.add_column("Dự đoán", style="yellow", justify="center")
    table.add_column("Đúng/Sai", style="green", justify="center")
    table.add_column("Độ chính xác", style="bold", justify="center")
    for strategy, prediction in individuals.items():
        correct_count = strategy_stats[strategy]["correct"]
        total_count = strategy_stats[strategy]["total"]
        acc = (correct_count / total_count) * 100 if total_count > 0 else 0
        match = "✅" if prediction == current_result else "❌"
        table.add_row(strategy, prediction, match, f"{acc:.1f}%")
    console.clear()
    console.print(table)
    console.print(f"[bold blue]👉 Kết quả phiên {session_id}: {current_result}[/]")
    console.print(f"[bold green]🔮 Dự đoán tiếp theo ({session_id + 1}): {final_prediction}[/]")
    console.print(f"[bold white]📊 Tổng độ chính xác: {accuracy:.1f}% ({correct}/{correct + wrong})[/]")
    console.print(f"[dim]🕒 Giờ VN: {get_vn_time()}[/]")


def predict_and_send(data):
    global last_prediction, last_prediction_session_id
    global correct, wrong, last_sent_session_id

    current = data[0]
    session_id = current["SessionId"]
    total = current["FirstDice"] + current["SecondDice"] + current["ThirdDice"]
    current_result = get_result(total)

    if last_sent_session_id is None:
        last_sent_session_id = session_id - 1

    if session_id == last_sent_session_id:
        return

    last_sent_session_id = session_id
    msg = ""

    if last_prediction and last_prediction_session_id == session_id - 1:
        is_correct = last_prediction == current_result
        if is_correct:
            correct += 1
        else:
            wrong += 1

        final_prediction, individuals = get_final_prediction(data)

        for s, res in individuals.items():
            strategy_stats[s]["total"] += 1
            if res == current_result:
                strategy_stats[s]["correct"] += 1

        accuracy = correct * 100 / (correct + wrong)
        detail = ""
        for s in strategies:
            acc = (
                strategy_stats[s]["correct"] * 100 / strategy_stats[s]["total"]
                if strategy_stats[s]["total"]
                else 0
            )
            detail += f"- {s}: {individuals[s]} ({acc:.1f}%)\n"

        msg = f"""🎯 *TOOL TỔNG HỢP CHIẾN THUẬT* 🎯
🆔 Phiên: {session_id}
🎲 Kết quả: {current['FirstDice']}-{current['SecondDice']}-{current['ThirdDice']} ➜ *{current_result}*

📌 Dự đoán phiên trước ({last_prediction_session_id}): *{last_prediction}* → {"✅ ĐÚNG" if is_correct else "❌ SAI"}
🧠 Dự đoán từng chiến thuật:
{detail}
🔮 Dự đoán tiếp theo ({session_id + 1}): *{final_prediction}*
📊 Độ chính xác tổng: *{accuracy:.1f}%* ({correct}/{correct + wrong})
🕒 Giờ VN: {get_vn_time()}
"""
        display_to_console(session_id, current_result, final_prediction, individuals, accuracy)
        last_prediction = final_prediction
        last_prediction_session_id = session_id
    else:
        final_prediction, _ = get_final_prediction(data)
        last_prediction = final_prediction
        last_prediction_session_id = session_id

    if is_bot_enabled and msg.strip():
        send_telegram_message(msg.strip())


def main():
    while True:
        console.print("[cyan]⏳ Đang fetch dữ liệu...[/]")
        data = fetch_data()
        if len(data) >= 2:
            predict_and_send(data)
        check_telegram_command()
        time.sleep(10)


if __name__ == "__main__":
    main()
