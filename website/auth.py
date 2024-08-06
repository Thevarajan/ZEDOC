from flask import Blueprint, render_template, redirect, request
from .models import db_login, db_signup

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        logresult = db_login(username, password)

        if logresult is None:
            error = "The details entered are incorrect"

        else:
            return redirect('/dashboard')

    return render_template("new_open.html", error=error)

@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        age = request.form.get('age')
        password = request.form.get('password')

        existing_user = db_login(username, password)

        if existing_user is not None:
            error = "Username already in use. Please choose another username."
        else:
            db_signup(username, age, password)
            return redirect('/login')

    return render_template("new_signup.html", error=error)

@auth.route('/dashboard')
def dashboard():
    return render_template("new_dash.html")


