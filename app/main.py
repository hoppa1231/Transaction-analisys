from flask import Flask, request, jsonify, render_template
from utils.frame_tools import filter_price

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get/operations', methods=['POST'])
def operation():
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    sign = data.get('sign')

    operations_list, total = filter_price(start_date, end_date, sign)

    operation_dict = {'operations': operations_list, 'total': total}
    return jsonify(operation_dict)

if __name__ == '__main__':
    app.run(debug=True)