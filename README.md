
# 🍽️ Food Pulse — AI-Powered Food Redistribution Platform

### 🌍 Overview
**Food Pulse** is a web application designed to bridge the gap between **restaurants**, **NGOs**, and **old-age homes** to minimize **food wastage**.  
It uses **AI-driven freshness prediction** and a built-in **FAQ + AI chatbot** to ensure surplus food is redistributed safely and efficiently.

---

## ✨ Key Features
- 🧠 **AI-Powered Shelf Life Prediction:**  
  Uses Groq’s **LLaMA-3.3-70B Versatile** model to estimate freshness duration (in hours) of any food item.
- 🤖 **Smart Hybrid Chatbot (FoodPulseChatbot):**  
  Combines FAQ-based responses with real-time AI chat via Groq API for accurate, context-aware assistance.
- 🍴 **Restaurant Dashboard:**  
  Restaurants can list surplus food and track freshness automatically.
- 🏠 **NGO / Old Age Home Dashboard:**  
  NGOs can view, claim, and collect food items safely.
- 🧑‍💼 **Admin Dashboard:**  
  Admins can oversee users, listings, and platform activity.
- 🔐 **Secure Authentication:**  
  Passwords are hashed securely using `werkzeug.security`.

---

## 🧩 Project Structure
```

📁 DBMS FINAL WEB/
│
├── 📂 static/               # Static assets (CSS, JS, images)
├── 📂 templates/            # HTML templates for Flask
├── 📄 app.py                # Main Flask application
├── 📄 chatbot.py            # Hybrid FAQ + AI Chatbot logic
├── 📄 database.db           # SQLite3 database
├── 📄 init_db.py            # Database initialization script
├── 📄 schema.sql            # SQL schema for tables
├── 📄 .env                  # Environment variables (Groq API key)
├── 📄 .gitignore            # Git ignore configuration
└── 📁 **pycache**/          # Auto-generated Python cache files

````

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/food-pulse.git
cd "DBMS FINAL WEB"
````

### 2️⃣ Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # For Linux/Mac
venv\Scripts\activate        # For Windows
```

### 3️⃣ Install Dependencies

```bash
pip install flask groq python-dotenv werkzeug requests
```

### 4️⃣ Setup Environment Variables

Create a `.env` file in the root directory:

```
GROQ_API_KEY=your_groq_api_key_here
FLASK_ENV=development
```

### 5️⃣ Initialize the Database

```bash
python init_db.py
```

This script executes `schema.sql` and creates the `database.db` file.

---

## 🚀 Run the Application

```bash
python app.py
```

Then open your browser and visit 👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧠 AI Freshness Prediction (Groq Integration)

* When a restaurant adds food, the system calls **Groq’s LLaMA-3.3 model** to estimate its safe shelf life in hours.
* The freshness duration (`fresh_until`) is computed automatically and stored in the database.
* Once expired, listings are automatically marked *Expired*.

---

## 💾 Database Overview

### 🧍 `users` Table

| Column              | Type    | Description                             |
| ------------------- | ------- | --------------------------------------- |
| id                  | INTEGER | Primary key                             |
| name                | TEXT    | User’s name                             |
| email               | TEXT    | Unique email                            |
| password            | TEXT    | Hashed password                         |
| account_type        | TEXT    | restaurant / ngo / old-age-home / admin |
| address             | TEXT    | Address of organization                 |
| phone_number        | TEXT    | Contact number                          |
| is_profile_complete | INTEGER | 1 if user added details                 |

### 🍱 `food_listings` Table

| Column        | Type     | Description                      |
| ------------- | -------- | -------------------------------- |
| id            | INTEGER  | Primary key                      |
| restaurant_id | INTEGER  | ID of restaurant                 |
| food_item     | TEXT     | Item name                        |
| quantity      | TEXT     | Quantity info                    |
| status        | TEXT     | Available / Claimed / Expired    |
| fresh_until   | DATETIME | Calculated freshness expiry      |
| claimed_by_id | INTEGER  | NGO/Old-age-home that claimed it |
| timestamp     | DATETIME | Time when food was listed        |

---

## 🤖 FoodPulseChatbot Overview

### 🔹 How It Works

The chatbot combines **instant FAQ answers** with **AI-powered responses** from the **Groq API**:

1. First checks against a **local FAQ dataset** (organized by category).
2. If no strong match is found, it dynamically queries **Groq’s LLaMA 3.1 model** using contextual information about the Food Pulse platform.
3. It uses **conversation history**, **rate limiting**, and **keyword filtering** to stay accurate and efficient.

### 🔹 Built-In Capabilities

* 🧩 **FAQ Matching:**
  Matches user queries with a curated set of pre-defined questions and answers (e.g., registration, logistics, food safety).
* 💬 **AI Context Replies:**
  Falls back to Groq API with a structured system prompt that includes Food Pulse’s documentation and mission.
* ⚙️ **Rate Limiting:**
  Prevents abuse (1 request/second, 100 requests/day limit).
* 🧠 **Memory:**
  Retains the last 6 exchanges for contextual understanding.
* 🧹 **Topic Filtering:**
  Ignores unrelated queries and redirects the user politely.

---

## 💬 Chat Endpoint

### 🔸 Route

`POST /chat`

### 🔸 Request Format

```json
{
  "message": "How can NGOs request food donations?"
}
```

### 🔸 Example Response

```json
{
  "reply": "NGOs can browse approved listings, filter based on their needs, and click 'Request' to claim an item. The restaurant receives a notification, and upon confirmation, pickup or delivery arrangements can be made."
}
```

If the question is outside the FAQ, the chatbot will automatically fetch a contextual AI response using Groq API.

---

## 🧩 Flask Template Mapping

| Template                    | Purpose                              |
| --------------------------- | ------------------------------------ |
| `index.html`                | Landing page                         |
| `login.html`                | Login and signup                     |
| `restaurant_dashboard.html` | Dashboard for restaurants            |
| `ngo_dashboard.html`        | Dashboard for NGOs and old-age homes |
| `admin_dashboard.html`      | Admin overview panel                 |
| `profile.html`              | User profile setup                   |

---

## 🪄 Future Enhancements

* 🧾 Add donation tracking and feedback system
* 📦 Introduce geolocation-based restaurant–NGO matching
* ⚡ Integrate real-time freshness sensors via IoT
* 🤖 Make chatbot context-aware with multi-turn reasoning
* 📈 Add analytics for food distribution impact

---

## 👨‍💻 Contributors

**Developed by:** *Spandan Chakraborty, Sarbatriki Jana, Souhardya Ray, Sreejani Banik & Saraddyuti Chakravarty*

**Focus Areas:** AI Integration, Backend Logic, and Sustainable Solutions

---

## 🪪 License

This project is licensed under the **MIT License** — free to use, modify, and distribute with proper attribution.

---

### 💚 *“Crafting a Seamless Bridge Between Restaurants, NGOs & Communities — Powered by AI.”*




