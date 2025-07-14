from flask import Flask, jsonify
import time
import requests
import re

app = Flask(__name__)

TASKS = {
    "m88":   ('M88',    'https://bet88ec.com/cach-danh-bai-sam-loc',      'https://bet88ec.com/',     'taodeptrai'),
    "fb88":  ('FB88',   'https://fb88mg.com/ty-le-cuoc-hong-kong-la-gi',  'https://fb88mg.com/',      'taodeptrai'),
    "188bet":('188BET', 'https://88betag.com/cach-choi-game-bai-pok-deng', 'https://88betag.com/',    'taodeptrailamnhe'),
    "w88":   ('W88',    'https://188.166.185.213/tim-hieu-khai-niem-3-bet-trong-poker-la-gi', 'https://188.166.185.213/', 'taodeptrai'),
    "v9bet": ('V9BET',  'https://v9betse.com/ca-cuoc-dua-cho',            'https://v9betse.com/',     'taodeptrai'),
    "bk8":   ('BK8',    'https://bk8ze.com/cach-choi-bai-catte',          'https://bk8ze.com/',       'taodeptrai'),
}

def get_real_code(key):
    name, url, ref, code_key = TASKS[key]
    try:
        res = requests.post(
            f'https://traffic-user.net/GET_MA.php?codexn={code_key}&url={url}&loai_traffic={ref}&clk=1000',
            timeout=20
        )
        match = re.search(r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>', res.text)
        if match:
            return match.group(1)
        else:
            return "Không tìm thấy mã"
    except Exception as e:
        return f"Lỗi: {e}"

@app.route('/api/bypass/all', methods=['GET'])
def bypass_all():
    time.sleep(1)
    result = {}
    for key in TASKS:
        result[key] = {
            "name": TASKS[key][0],
            "code": get_real_code(key)
        }
    return jsonify({
        "success": True,
        "results": result
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Not Found",
        "message": "Endpoint không tồn tại. Vui lòng kiểm tra lại đường dẫn."
    }), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)