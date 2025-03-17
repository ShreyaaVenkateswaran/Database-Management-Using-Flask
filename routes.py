from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from models import mysql, get_user_by_email

app_routes = Blueprint("app_routes", __name__)
bcrypt = Bcrypt()

@app_routes.route("/")
def home():
    return render_template("index.html")

@app_routes.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        mysql.connection.commit()
        cur.close()

        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("app_routes.login"))

    return render_template("signup.html")

@app_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = get_user_by_email(email)

        if user and bcrypt.check_password_hash(user["password"], password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("app_routes.dashboard"))

        flash("Invalid credentials. Try again.", "danger")

    return render_template("login.html")

@app_routes.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.username)

@app_routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("app_routes.login"))
