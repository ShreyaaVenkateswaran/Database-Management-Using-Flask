from flask import Flask, render_template
from config import Config
from extensions import db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.grades import grades_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(grades_bp)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)