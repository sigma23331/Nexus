from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # 初始阶段开启跨域，方便调试

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "online",
        "message": "心运岛后端已就绪",
        "version": "v0.1.0-skeleton"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)