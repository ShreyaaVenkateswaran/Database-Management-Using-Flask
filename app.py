from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = "secret123*"

# ✅ MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306  # Change to 3307 if needed
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Krishna3*'
app.config['MYSQL_DB'] = 'user_management'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ✅ User Model
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = mysql.connection
    if not conn:
        print("Database connection error!")  # Debugging
        return None

    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(user["id"], user["username"], user["email"])
    return None

# ✅ Home Page
@app.route('/')
def home():
    return render_template('home.html')

# ✅ Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        cur = mysql.connection.cursor()

        try:
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                        (username, email, hashed_password))
            mysql.connection.commit()

            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            user_id = cur.fetchone()

            if user_id:
                user_id = user_id['id']
            else:
                flash("Error: User ID not found after insertion!", "danger")
                return redirect(url_for('register'))

            # ✅ Insert default grades using loop
            subjects = ['Mathematics', 'Science', 'English', 'PE', 'Hindi', 'Tamil']
            grades = ['A+', 'A', 'A+', 'B', 'B-', 'A+']

            for subject, grade in zip(subjects, grades):
                cur.execute("INSERT INTO grades (user_id, subject, grade) VALUES (%s, %s, %s)", 
                            (user_id, subject, grade))

            mysql.connection.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('login'))

        except Exception as e:
            mysql.connection.rollback()
            flash("Database error: " + str(e), "danger")
        finally:
            cur.close()

    return render_template('register.html')

# ✅ Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            print("Stored Password Hash:", user['password'])  # Debugging line

            if bcrypt.check_password_hash(user['password'], password):  
                user_obj = User(user["id"], user["username"], user["email"])
                login_user(user_obj)
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
        else:
            flash('User not found.', 'danger')

    return render_template('login.html')

# ✅ Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ✅ Dashboard (Users can see their grades)
@app.route('/dashboard')
@login_required
def dashboard():
    conn = mysql.connection
    conn.ping(True)  # ✅ Auto-reconnect if connection is lost

    cur = conn.cursor()
    cur.execute("SELECT subject, grade FROM grades WHERE user_id = %s", (current_user.id,))
    grades = cur.fetchall()
    cur.close()

    return render_template('dashboard.html', username=current_user.username, grades=grades)

# ✅ Check MySQL Connection Before Running
with app.app_context():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()
        cur.close()
        print(f"Database connection successful! Users count: {count['COUNT(*)']}")
    except Exception as e:
        print("Database Connection Error:", str(e))

# ✅ Run App
if __name__ == '__main__':
    app.run(debug=True)
