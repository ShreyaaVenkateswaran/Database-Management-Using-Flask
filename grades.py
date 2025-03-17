from flask import Blueprint, render_template, session
from models.user import Grade

grades_bp = Blueprint('grades', __name__)

@grades_bp.route('/grades')
def grades():
    user_id = session.get('user_id')
    if user_id:
        grades = Grade.query.filter_by(user_id=user_id).all()
        return render_template('grades.html', grades=grades)
    return "User not logged in", 404