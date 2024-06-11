from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3306/app_caisse'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    # Ajoutez d'autres attributs si nécessaire


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fee_id = db.Column(db.Integer, db.ForeignKey('fee.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_paid = db.Column(db.DateTime, nullable=False)
    # Ajoutez d'autres attributs si nécessaire


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    # Ajoutez d'autres attributs si nécessaire


class Refund(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(500), nullable=False)
    # Ajoutez d'autres attributs si nécessaire


class Scholarship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    # Ajoutez d'autres attributs si nécessaire


class StudentData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    program = db.Column(db.String(100), nullable=False)
    credits_earned = db.Column(db.Integer, nullable=False)
    # Ajoutez d'autres attributs si nécessaire


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Ajoutez les attributs nécessaires pour le rapport


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Connexion réussie
            return redirect(url_for('profile'))  # Rediriger vers le profil de l'utilisateur
        else:
            # Informations d'identification incorrectes
            error = 'Nom d\'utilisateur ou mot de passe incorrect.'
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error = 'Ce nom d\'utilisateur est déjà utilisé.'
            return render_template('register.html', error=error)

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/profile')
def profile():
    # Récupérer les informations de l'utilisateur depuis la base de données
    user = User.query.get(1)  # Remplacez 1 par l'ID de l'utilisateur connecté
    return render_template('profile.html', user=user)


@app.route('/fees')
def fees():
    # Récupérer tous les frais académiques depuis la base de données
    fees = Fee.query.all()
    return render_template('fees.html', fees=fees)


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        # Récupérer les données du formulaire de paiement
        fee_id = request.form.get('fee_id')
        amount = request.form.get('amount')
        # Créer une nouvelle instance de paiement et l'ajouter à la base de données
        payment = Payment(user_id=1, fee_id=fee_id, amount=amount,
                          date_paid=datetime.now())  # Remplacez 1 par l'ID de l'utilisateur connecté
        db.session.add(payment)
        db.session.commit()
        return redirect(url_for('history'))  # Rediriger vers l'historique des paiements
    else:
        # Récupérer les frais académiques depuis la base de données pour affichage dans le formulaire de paiement
        fees = Fee.query.all()
        return render_template('payment.html', fees=fees)


@app.route('/history')
def history():
    # Récupérer tous les paiements effectués par l'utilisateur depuis la base de données
    payments = Payment.query.filter_by(
        user_id=1).all()  # RemOops, il semble que le code ait été coupé à la fin. Voici la suite du code :
    return render_template('history.html', payments=payments)


@app.route('/notifications')
def notifications():
    # Récupérer toutes les notifications de l'utilisateur depuis la base de données
    notifications = Notification.query.filter_by(user_id=1).all()  # Remplacez 1 par l'ID de l'utilisateur connecté
    return render_template('notifications.html', notifications=notifications)


@app.route('/refunds')
def refunds():
    # Récupérer tous les remboursements demandés par l'utilisateur depuis la base de données
    refunds = Refund.query.filter_by(user_id=1).all()  # Remplacez 1 par l'ID de l'utilisateur connecté
    return render_template('refunds.html', refunds=refunds)


@app.route('/scholarships')
def scholarships():
    # Récupérer toutes les bourses disponibles depuis la base de données
    scholarships = Scholarship.query.all()
    return render_template('scholarships.html', scholarships=scholarships)


@app.route('/student_data')
def student_data():
    # Récupérer les données de l'étudiant depuis la base de données
    student_data = StudentData.query.filter_by(user_id=1).first()  # Remplacez 1 par l'ID de l'utilisateur connecté
    return render_template('student_data.html', student_data=student_data)


@app.route('/reports')
def reports():
    # Récupérer tous les rapports depuis la base de données
    reports = Report.query.all()
    return render_template('reports.html', reports=reports)


if __name__ == '__main__':
    app.run()
