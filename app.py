import sqlite3
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from groq import Groq
from dotenv import load_dotenv
from flask import jsonify
from chatbot import FoodPulseChatbot

chatbot_instance = FoodPulseChatbot()


def adapt_datetime(dt):
    return dt.isoformat()

def convert_timestamp(ts):
    return datetime.fromisoformat(ts.decode('utf-8'))


sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("timestamp", convert_timestamp)
sqlite3.register_converter("datetime", convert_timestamp)



# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = 'database.db'

# Initialize Groq Client
try:
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    print(f"Failed to initialize Groq client: {e}")
    groq_client = None

# Database Connection Management
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Groq Function to get food freshness
def get_food_freshness_duration(food_item_name):
    if not groq_client:
        print("Groq client not available. Defaulting to 48 hours.")
        return 48

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a food safety expert. Your task is to estimate the safe consumption shelf life of a food item in hours, assuming it's prepared and stored correctly at room/refrigerated temperature. Respond with ONLY an integer representing the number of hours. Do not add any other text, explanation, or units."
                },
                {
                    "role": "user",
                    "content": f"Food item: '{food_item_name}'. How many hours does it stay fresh?"
                }
            ],
            # --- MODIFIED: Switched to a currently supported model ---
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )
        response_text = chat_completion.choices[0].message.content.strip()
        return int(response_text)
    except Exception as e:
        print(f"Groq API call failed or returned invalid data: {e}. Defaulting to 48 hours.")
        return 48



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['signup-name']
    email = request.form['signup-email']
    account_type = request.form['signup-type']
    password = request.form['signup-password']
    confirm_password = request.form['signup-confirm-password']

    if password != confirm_password:
        return redirect(url_for('login_page'))

    hashed_password = generate_password_hash(password)
    db = get_db()
    try:
        db.execute(
            'INSERT INTO users (name, email, password, account_type) VALUES (?, ?, ?, ?)',
            (name, email, hashed_password, account_type)
        )
        db.commit()
    except sqlite3.IntegrityError:
        return redirect(url_for('login_page'))
    
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form['login-email']
        password = request.form['login-password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['account_type'] = user['account_type']
            session['is_profile_complete'] = user['is_profile_complete']
            if not session['is_profile_complete']:
                return redirect(url_for('profile'))
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid email or password.")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    if not session.get('is_profile_complete'):
        return redirect(url_for('profile'))

    db = get_db()
    account_type = session['account_type']
    
    expiration_check_sql = "CASE WHEN DATETIME('now', 'localtime') > fresh_until THEN 'Expired' ELSE status END as current_status"

    if account_type == 'restaurant':
        listings = db.execute(
            f'SELECT *, {expiration_check_sql} FROM food_listings WHERE restaurant_id = ? ORDER BY timestamp DESC',
            (session['user_id'],)
        ).fetchall()
        return render_template('restaurant_dashboard.html', listings=listings)

    elif account_type in ['ngo', 'old-age-home']:
        listings = db.execute(
            f"""
            SELECT fl.*, u.name as restaurant_name, u.address as restaurant_address, {expiration_check_sql}
            FROM food_listings fl
            JOIN users u ON fl.restaurant_id = u.id
            WHERE fl.status != 'Claimed'
            ORDER BY fl.timestamp DESC
            """
        ).fetchall()
        return render_template('ngo_dashboard.html', listings=listings)

    elif account_type == 'admin':
        restaurants = db.execute("SELECT name, email, address, phone_number FROM users WHERE account_type = 'restaurant'").fetchall()
        ngos = db.execute("SELECT name, email, address, phone_number FROM users WHERE account_type IN ('ngo', 'old-age-home')").fetchall()
        listings = db.execute(
            f"""
            SELECT fl.*, u.name as restaurant_name, {expiration_check_sql}
            FROM food_listings fl JOIN users u ON fl.restaurant_id = u.id 
            ORDER BY fl.timestamp DESC
            """
        ).fetchall()
        return render_template('admin_dashboard.html', restaurants=restaurants, ngos=ngos, listings=listings)

    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    db = get_db()
    if request.method == 'POST':
        address = request.form['address']
        phone_number = request.form['phone_number']
        db.execute(
            'UPDATE users SET address = ?, phone_number = ?, is_profile_complete = 1 WHERE id = ?',
            (address, phone_number, session['user_id'])
        )
        db.commit()
        session['is_profile_complete'] = 1
        return redirect(url_for('dashboard'))
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return render_template('profile.html', user=user)

@app.route('/add_food', methods=['POST'])
def add_food():
    if 'user_id' not in session or session['account_type'] != 'restaurant':
        return redirect(url_for('login_page'))
    
    food_item = request.form['food_item']
    quantity = request.form['quantity']
    restaurant_id = session['user_id']
    
    hours_to_be_fresh = get_food_freshness_duration(food_item)
    
    current_time = datetime.now()
    fresh_until_time = current_time + timedelta(hours=hours_to_be_fresh)
    
    db = get_db()
    db.execute(
        'INSERT INTO food_listings (restaurant_id, food_item, quantity, fresh_until) VALUES (?, ?, ?, ?)',
        (restaurant_id, food_item, quantity, fresh_until_time)
    )
    db.commit()
    return redirect(url_for('dashboard'))

@app.route('/claim_food/<int:listing_id>', methods=['POST'])
def claim_food(listing_id):
    if 'user_id' not in session or session['account_type'] not in ['ngo', 'old-age-home']:
        return redirect(url_for('login_page'))
    db = get_db()
    db.execute(
        "UPDATE food_listings SET status = 'Claimed', claimed_by_id = ? WHERE id = ?",
        (session['user_id'], listing_id)
    )
    db.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/chat', methods=['POST'])
def chat():
    # Ensure the request is in the correct format (JSON)
    if not request.is_json:
        return jsonify({"error": "Invalid request: must be JSON"}), 400

    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Use the chatbot instance to get a response
    ai_response = chatbot_instance.generate_response(user_message)
    return jsonify({'reply': ai_response})

if __name__ == '__main__':
    app.run(debug=True)