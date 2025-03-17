from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User
from extensions import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('dashboard.html', user=user)
    return "User not logged in", 404

@dashboard_bp.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    user_id = session.get('user_id')
    if not user_id:
        return "User not logged in", 404

    user = User.query.get(user_id)
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_email = request.form.get('email')

        if new_username:
            user.username = new_username
        if new_email:
            user.email = new_email

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('update_profile.html', user=user)