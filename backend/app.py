from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # 开发环境开启跨域

@app.route('/api/test')
def test():
    return jsonify({
        "message": "来自服务器后端的慰藉：连接成功！",
        "status": "success"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)