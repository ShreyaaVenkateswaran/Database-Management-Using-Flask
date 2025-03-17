from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User, Grade
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the user already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists', 'error')
        else:
            # Create a new user
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            # Add sample grades for the new user
            sample_grades = [
                Grade(user_id=new_user.id, subject='Math', grade='A+'),
                Grade(user_id=new_user.id, subject='Science', grade='A'),
                Grade(user_id=new_user.id, subject='History', grade='A'),
                Grade(user_id=new_user.id, subject='Hindi', grade='B'),
                Grade(user_id=new_user.id, subject='English', grade='A+'),
                Grade(user_id=new_user.id, subject='PE', grade='B'),
                Grade(user_id=new_user.id, subject='Tamil', grade='A+'),
            ]
            db.session.add_all(sample_grades)
            db.session.commit()

            # Log the user in after registration
            session['user_id'] = new_user.id
            flash('Account created and login successful!', 'success')
            return redirect(url_for('dashboard.dashboard'))

    return render_template('signup.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))