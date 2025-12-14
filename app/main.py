import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import utils.frame_tools as ft
from utils import BASE_DIR

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'pdf', 'csv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get/operations', methods=['POST'])
def operation():
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    sign = data.get('sign')

    operations_list, total = ft.filter_price(start_date, end_date, sign)

    operation_dict = {'operations': operations_list, 'total': total}
    return jsonify(operation_dict)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Файл не найден'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Пустое имя файла'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': 'Допустимые расширения: pdf, csv'}), 400

        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()

        if ext == 'pdf':
            save_dir = os.path.join(BASE_DIR, 'data', 'pdf')
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, filename)
            print(save_path)
            file.save(save_path)
            ft.refresh_data_from_pdf(filename=filename, input_path=save_path)
        else:
            # CSV: write directly to output.csv
            save_dir = os.path.join(BASE_DIR, 'data', 'base')
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, 'output.csv')
            file.save(save_path)
            ft.init_dataFrame()

        return jsonify({'status': 'ok', 'rows': len(ft.df)})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500

if __name__ == '__main__':
    app.run(debug=True)
