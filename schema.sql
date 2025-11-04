-- Table for users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    account_type TEXT NOT NULL,
    address TEXT,
    phone_number TEXT,
    is_profile_complete BOOLEAN DEFAULT 0
);

-- Table for food listings by restaurants

CREATE TABLE IF NOT EXISTS food_listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER NOT NULL,
    food_item TEXT NOT NULL,
    quantity TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Available', -- e.g., Available, Claimed, Expired
    claimed_by_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    fresh_until DATETIME, -- <-- ADD THIS LINE
    FOREIGN KEY (restaurant_id) REFERENCES users (id),
    FOREIGN KEY (claimed_by_id) REFERENCES users (id)
);