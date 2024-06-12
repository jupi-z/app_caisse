import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = '621227087952085300224466'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'app_caisse'
db = MySQL(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Identifiant ou code incorrect')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        cursor = db.connection.cursor()
        cursor.execute(
            "INSERT INTO User (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        db.connection.commit()
        cursor.close()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/profile')
@login_required
def profile():
    user_id = session['username']
    cursor = db.connection.cursor()
    cursor.execute(f"SELECT * FROM User WHERE username = '{user_id}'")
    user = cursor.fetchone()
    cursor.close()
    return render_template('profile.html', user=user)


@app.route('/fees')
@login_required
def fees():
    cursor = db.connection.cursor()
    cursor.execute("SELECT * FROM Fee")
    fees = cursor.fetchall()
    cursor.close()
    return render_template('fees.html', fees=fees)


@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if request.method == 'POST':
        fee_id = request.form.get('fee_id')
        amount = request.form.get('amount')
        user_id = session['username']
        cursor = db.connection.cursor()
        cursor.execute(
            f"INSERT INTO Payment (user_id, fee_id, amount, date_paid) VALUES ('{user_id}', '{fee_id}', '{amount}', NOW())")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('history'))
    else:
        cursor = db.connection.cursor()
        cursor.execute("SELECT * FROM Fee")
        fees = cursor.fetchall()
        cursor.close()
        return render_template('payment.html', fees=fees)


@app.route('/history')
@login_required
def history():
    user_id = session['username']
    cursor = db.connection.cursor()
    cursor.execute(f"SELECT * FROM Payment WHERE user_id = '{user_id}'")
    payments = cursor.fetchall()
    cursor.close()
    return render_template('history.html', payments=payments)


@app.route('/notifications')
@login_required
def notifications():
    user_id = session['username']
    cursor = db.connection.cursor()
    cursor.execute(f"SELECT * FROM Notification WHERE user_id = '{user_id}'")
    notifications = cursor.fetchall()
    cursor.close()
    return render_template('notifications.html', notifications=notifications)


@app.route('/refunds')
@login_required
def refunds():
    user_id = session['username']
    cursor = db.connection.cursor()
    cursor.execute(f"SELECT * FROM Refund WHERE user_id = '{user_id}'")
    refunds = cursor.fetchall()
    cursor.close()
    return render_template('refunds.html', refunds=refunds)


@app.route('/scholarships')
@login_required
def scholarships():
    cursor = db.connection.cursor()
    cursor.execute("SELECT * FROM Scholarship")
    scholarships = cursor.fetchall()
    cursor.close()
    return render_template('scholarships.html', scholarships=scholarships)


@app.route('/student_data')
@login_required
def student_data():
    user_id = session['username']
    cursor = db.connection.cursor()
    cursor.execute(f"SELECT * FROM StudentData WHERE user_id = '{user_id}'")
    student_data = cursor.fetchone()
    cursor.close()
    return render_template('student_data.html', student_data=student_data)


@app.route('/reports')
@login_required
def reports():
    cursor = db.connection.cursor()
    cursor.execute("SELECT * FROM Report")
    reports = cursor.fetchall()
    cursor.close()
    return render_template('reports.html', reports=reports)


if __name__ == '__main__':
    app.run(debug=True)
