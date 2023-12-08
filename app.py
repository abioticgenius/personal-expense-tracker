from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import io
import base64
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
db = SQLAlchemy(app)
registered_users = {}


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(100), nullable=False)
    income = db.Column(db.Float, nullable=False)
    groceries = db.Column(db.Float, nullable=False)
    fuel = db.Column(db.Float, nullable=False)
    bills = db.Column(db.Float, nullable=False)
    rent = db.Column(db.Float, nullable=False)
    misc = db.Column(db.Float, nullable=False)
    savings = db.Column(db.Float, nullable=False)
    savings_percentage = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Expense %r>' % self.month


@app.route('/')
def index():
    expenses = Expense.query.all()
    total_savings = sum(expense.savings for expense in expenses)
    records = Expense.query.all()
    expenses = Expense.query.all()
    months = [record.month for record in records]

    savings_percentage = [expense.savings for expense in expenses]

    plt.plot(months, savings_percentage)
    plt.scatter(months, savings_percentage)
    plt.xlabel('Month')
    plt.ylabel('Savings Percentage')
    plt.title('Monthly Savings Percentage Compared to Previous Month')
    plt.xticks(rotation=45, ha="right")

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    img_str = base64.b64encode(img.read()).decode('utf-8')
    return render_template('index.html', expenses=expenses, total_savings=total_savings, img_str=img_str)


@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    congrats = None
    if request.method == 'POST':
        month = request.form['month']
        income = float(request.form['income'])
        groceries = float(request.form['groceries'])
        fuel = float(request.form['fuel'])
        bills = float(request.form['bills'])
        rent = float(request.form['rent'])
        misc = float(request.form['misc'])
        total_expenses = groceries + fuel + bills + rent + misc
        savings = income - total_expenses
        savings_percentage = savings / income * 100
        expense = Expense(month=month, income=income, groceries=groceries, fuel=fuel, bills=bills,
                          rent=rent, misc=misc, savings=savings, savings_percentage=savings_percentage)
        if savings_percentage > 20:
            # print a DOM element saying congrats
            congrats = "Congratulations on saving!"

        db.session.add(expense)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html', congrats=congrats)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    if request.method == 'POST':
        expense.month = request.form['month']
        expense.income = float(request.form['income'])
        expense.groceries = float(request.form['groceries'])
        expense.fuel = float(request.form['fuel'])
        expense.bills = float(request.form['bills'])
        expense.rent = float(request.form['rent'])
        expense.misc = float(request.form['misc'])
        total_expenses = expense.groceries + expense.fuel + \
            expense.bills + expense.rent + expense.misc
        expense.savings = expense.income - total_expenses
        expense.savings_percentage = expense.savings / expense.income * 100
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', expense=expense)


@app.route('/delete/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/plot_graph')
def plot_graph():
    records = Expense.query.order_by(Expense.month).all()
    expenses = Expense.query.all()
    months = [record.month for record in records]
    savings = [record.income - (record.groceries + record.fuel +
                                record.bills + record.rent + record.misc) for record in records]

    savings_percentage = [expense.savings for expense in expenses]

    plt.plot(months, savings_percentage)
    plt.scatter(months, savings_percentage)
    plt.xlabel('Month')
    plt.ylabel('Savings Percentage')
    plt.title('Monthly Savings Percentage Compared to Previous Month')
    plt.xticks(rotation=45, ha="right")

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    img_str = base64.b64encode(img.read()).decode('utf-8')

    return render_template('graph.html', img_str=img_str)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in registered_users and registered_users[username] == password:
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username not in registered_users:
            registered_users[username] = password
            return redirect(url_for('login'))
        else:
            error = 'Username already taken. Please choose another username.'
            return render_template('register.html', error=error)

    return render_template('register.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
