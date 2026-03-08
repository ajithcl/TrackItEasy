from datetime import datetime

from flask import request, jsonify, Flask
from Models.ExpenseModel import Expense
from flask_wtf.csrf import CSRFProtect

from Models.SettingsModel import Settings

app = Flask(__name__)
csrf = CSRFProtect(app)
settings_class = Settings()

# ─── GET Current Month Total Amount ───────────────────────────
@app.route('/api/expense/current_month/total', methods=['GET'])
def get_current_month_total():
    expense_class = Expense()
    expense_data =  jsonify(expense_class.getMonthlyExpenseCategorySplit(userid='Ajith'))
    return expense_data, 200

@csrf.exempt
@app.route('/api/expense/create', methods=['POST'])
def create_expense():
    data = request.get_json()
    data['ExpenseDate'] = datetime.strptime(data['ExpenseDate'], "%Y-%m-%d")
    category_code =  data['Category']

    category_cursor= settings_class.get_settings(userid='Ajith',  module= 'Expenses', attribute='Category')
    settings_records = list (category_cursor)
    expense_category_list = []
    for category in settings_records:
        expense_category_list.append(category['Content'])
    if category_code not in expense_category_list:
        return jsonify({"status": "error",
                        "message": "Invalid category code"}), 400

    expense_class = Expense()
    result = expense_class.createExpense(data)
    if result:
        return jsonify({"status": "success",
                        "message": "Expense created successfully", "id": str(result.inserted_id)}), 201
    else:
        return jsonify({"status": "error",
                        "message": "Failed to create expense",
                        "error": result}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)

