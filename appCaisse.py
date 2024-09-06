# Importation des bibliothèques nécessaires
import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Initialisation de l'application Flask
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = '62122708795208530022446'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'app_caisse'
db = MySQL(app)


# Définition du décorateur pour vérifier si l'utilisateur est connecté
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# Fonction pour vérifier la dernière activité de l'utilisateur
def check_user_activity():
    if 'last_activity' in session:
        last_activity = session['last_activity']
        if datetime.now() - last_activity > timedelta(minutes=5):
            session.pop('username', None)
            return jsonify({'status': 'inactive'})
    session['last_activity'] = datetime.now()
    return jsonify({'status': 'active'})


# Route pour la page d'accueil
@app.route('/')
def home():
    return render_template('home.html')


# Route pour la page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Utilisateur WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        if user and check_password_hash(user['mot_de_passe'], password):
            session['username'] = user['email']
            session['last_activity'] = datetime.now()
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Identifiant ou code incorrect')
    return render_template('login.html')


# Route pour la page d'inscription
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        cursor = db.connection.cursor()
        cursor.execute(
            "INSERT INTO Utilisateur (nom, prenom, email, mot_de_passe) VALUES (%s, %s, %s, %s)",
            (nom, prenom, email, hashed_password))
        db.connection.commit()
        cursor.close()
        return redirect(url_for('login'))
    return render_template('register.html')


# Route pour la page de déconnexion
@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


# Route pour le tableau de bord
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


# Route pour la page de profil
@app.route('/profile')
@login_required
def profile():
    user_email = session['username']
    cursor = db.connection.cursor()
    cursor.execute(f"SELECT * FROM Utilisateur WHERE email = '{user_email}'")
    user = cursor.fetchone()
    cursor.close()
    return render_template('profile.html', user=user)


# Route pour la page de paiement
@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if request.method == 'POST':
        fee_id = request.form.get('fee_id')
        amount = request.form.get('amount')
        user_email = session['username']
        cursor = db.connection.cursor()
        cursor.execute(
            f"INSERT INTO Paiement (etudiant_id, frais_id, montant, date_paiement, mode_paiement, reference_paiement, utilisateur_id) VALUES ((SELECT id FROM Etudiant WHERE email = '{user_email}'), '{fee_id}', '{amount}', NOW(), 'Cash', 'N/A', (SELECT id FROM Utilisateur WHERE email = '{user_email}'))")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('history'))
    else:
        cursor = db.connection.cursor()
        cursor.execute("SELECT * FROM Frais")
        fees = cursor.fetchall()
        cursor.close()
        return render_template('payment.html', fees=fees)


# Route pour la page de notifications
@app.route('/manage')
@login_required
def manage():
    cursor = db.connection.cursor()
    cursor.execute("SELECT * FROM Frais")
    fees = cursor.fetchall()
    cursor.close()
    return render_template('manage.html', fees=fees)


@app.route('/manage/add_fee', methods=['POST'])
@login_required
def add_fee():
    name = request.form['name']
    amount = request.form['amount']
    due_date = request.form['due_date']
    description = request.form['description']

    cursor = db.connection.cursor()
    cursor.execute("INSERT INTO Frais (nom, montant, date_echeance, description) VALUES (%s, %s, %s, %s)",
                   (name, amount, due_date, description))
    db.connection.commit()
    cursor.close()

    return redirect(url_for('manage'))


# Route pour la page de données étudiantes
@app.route('/student_data')
@login_required
def student_data():
    user_email = session['username']
    cursor = db.connection.cursor()
    cursor.execute(
        f"SELECT * FROM StudentData WHERE user_id = (SELECT id FROM Utilisateur WHERE email = '{user_email}')")
    student_data = cursor.fetchone()
    cursor.close()
    return render_template('student_data.html', student_data=student_data)


# Route pour vérifier l'activité de l'utilisateur
@app.route('/check_activity')
@login_required
def check_activity():
    return check_user_activity()


# Lancement de l'application
if __name__ == '__main__':
    app.run(debug=True)
