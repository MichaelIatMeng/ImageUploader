#!/usr/bin/python3
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import pymysql.cursors
import os
from PIL import Image
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
# MySQL数据库连接配置
connection = pymysql.connect(host='192.168.20.254',
                             user='admin',
                             password='Aa123456!',
                             database='Pre_Database_Proverbs',
                             cursorclass=pymysql.cursors.DictCursor)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    
@app.route('/upload', methods=['POST','GET'])
def upload_file():
    # 获取上传的文件列表
    files = []
    for key in request.files:
        if key.startswith('file'):
            files.append(request.files[key])

    # 获取输入的数字
    number = request.form.get('number')

    # 查询MySQL数据库中是否存在该数字及对应的path
    exists = False
    item_path = None
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Path WHERE item = %s"
            query = cursor.mogrify(sql,(number,))
            print("Full SQL Query:",query)
            cursor.execute(sql, (number,))
            result = cursor.fetchone()
            print(result)
            if result:
                exists = True
                item_path = result['path']
    except Exception as e:
        print("Error:", e)

    if not exists or not item_path:
        # 如果数字不存在或者对应的path不存在，则直接返回不存在
        return jsonify({
            'exists': False,
            'item_path': 'fail'
        })

    # 存储上传的文件
    filenames = []
    for file in files:
        print(file)
        if file:
            filename = file.filename
            file_path = os.path.join(item_path, filename)
            file.save(file_path)
            filenames.append(filename)
    # 将图片转换为JPG格式
    for filename in filenames:
        number1 = filename.split('.')[0]
        image_path = os.path.join(item_path, filename)
        image = Image.open(image_path)
        image.convert("RGB").save(os.path.join(item_path, f"IMG_{number}_{number1}.jpg"), "JPEG")
        os.remove(image_path)


    return jsonify({
        'filenames': filenames,
        'number': number,
        'exists': exists,
        'item_path': item_path
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)