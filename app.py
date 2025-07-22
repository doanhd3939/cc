from flask import Flask, jsonify
import time
import requests
import re
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    """Lấy mã thực từ API traffic-user.net"""
    name, url, ref, code_key = TASKS[key]
    try:
        logger.info(f"Đang lấy mã cho {name}...")
        res = requests.post(
            f'https://traffic-user.net/GET_MA.php?codexn={code_key}&url={url}&loai_traffic={ref}&clk=1000',
            timeout=20,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        match = re.search(r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>', res.text)
        if match:
            code = match.group(1)
            logger.info(f"Lấy mã thành công cho {name}: {code}")
            return code
        else:
            logger.warning(f"Không tìm thấy mã cho {name}")
            return "Không tìm thấy mã"
    except requests.RequestException as e:
        logger.error(f"Lỗi kết nối khi lấy mã cho {name}: {e}")
        return f"Lỗi kết nối: {e}"
    except Exception as e:
        logger.error(f"Lỗi không xác định khi lấy mã cho {name}: {e}")
        return f"Lỗi: {e}"

@app.route('/', methods=['GET'])
def home():
    """Trang chủ API"""
    return jsonify({
        "success": True,
        "message": "API Bypass đang hoạt động",
        "endpoints": {
            "/api/bypass/all": "Lấy tất cả mã bypass",
            "/api/bypass/<key>": "Lấy mã bypass cho một site cụ thể",
            "/api/sites": "Danh sách các site có sẵn"
        },
        "available_sites": list(TASKS.keys())
    })

@app.route('/api/sites', methods=['GET'])
def get_sites():
    """Lấy danh sách các site có sẵn"""
    sites = {}
    for key, (name, url, ref, code_key) in TASKS.items():
        sites[key] = {
            "name": name,
            "url": url,
            "ref": ref
        }
    return jsonify({
        "success": True,
        "sites": sites,
        "total": len(sites)
    })

@app.route('/api/bypass/<key>', methods=['GET'])
def bypass_single(key):
    """Lấy mã bypass cho một site cụ thể"""
    if key not in TASKS:
        return jsonify({
            "success": False,
            "error": "Site không tồn tại",
            "message": f"Site '{key}' không có trong danh sách. Các site có sẵn: {list(TASKS.keys())}"
        }), 404
    
    try:
        time.sleep(0.5)  # Giảm thời gian chờ cho single request
        name = TASKS[key][0]
        code = get_real_code(key)
        
        return jsonify({
            "success": True,
            "site": key,
            "name": name,
            "code": code,
            "timestamp": int(time.time())
        })
    except Exception as e:
        logger.error(f"Lỗi khi xử lý request cho {key}: {e}")
        return jsonify({
            "success": False,
            "error": "Lỗi server",
            "message": str(e)
        }), 500

@app.route('/api/bypass/all', methods=['GET'])
def bypass_all():
    """Lấy tất cả mã bypass"""
    try:
        time.sleep(1)
        result = {}
        errors = []
        
        for key in TASKS:
            try:
                name = TASKS[key][0]
                code = get_real_code(key)
                result[key] = {
                    "name": name,
                    "code": code,
                    "timestamp": int(time.time())
                }
            except Exception as e:
                errors.append(f"Lỗi khi lấy mã cho {key}: {e}")
                result[key] = {
                    "name": TASKS[key][0],
                    "code": f"Lỗi: {e}",
                    "timestamp": int(time.time())
                }
        
        response_data = {
            "success": True,
            "results": result,
            "total": len(result),
            "timestamp": int(time.time())
        }
        
        if errors:
            response_data["warnings"] = errors
            
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Lỗi nghiêm trọng trong bypass_all: {e}")
        return jsonify({
            "success": False,
            "error": "Lỗi server nghiêm trọng",
            "message": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint cho monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": int(time.time()),
        "service": "API Bypass"
    })

@app.errorhandler(404)
def not_found(e):
    """Xử lý lỗi 404"""
    return jsonify({
        "success": False,
        "error": "Not Found",
        "message": "Endpoint không tồn tại. Vui lòng kiểm tra lại đường dẫn.",
        "available_endpoints": [
            "/",
            "/api/bypass/all",
            "/api/bypass/<key>",
            "/api/sites",
            "/health"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """Xử lý lỗi 500"""
    logger.error(f"Lỗi server 500: {e}")
    return jsonify({
        "success": False,
        "error": "Internal Server Error",
        "message": "Đã xảy ra lỗi server. Vui lòng thử lại sau."
    }), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)
