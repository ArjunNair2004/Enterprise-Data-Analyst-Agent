-- STREAMING_CHUNK: Cleaning up existing tables...
-- Drop tables if they exist (useful for resetting the environment)
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS users;

-- STREAMING_CHUNK: Creating Users table...
-- 1. Create Users Table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    signup_date DATE NOT NULL,
    acquisition_channel VARCHAR(50) -- e.g., 'Organic', 'Paid Search', 'Referral'
);

-- STREAMING_CHUNK: Creating Orders table...
-- 2. Create Orders Table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL, -- e.g., 'completed', 'refunded', 'pending'
    gross_amount DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00
);

-- STREAMING_CHUNK: Inserting seed data into Users...
-- 3. Insert Dummy Data
INSERT INTO users (full_name, email, signup_date, acquisition_channel) VALUES
('Alice Smith', 'alice@example.com', '2026-01-15', 'Organic'),
('Bob Johnson', 'bob@example.com', '2026-02-20', 'Paid Search'),
('Charlie Brown', 'charlie@example.com', '2026-03-05', 'Referral'),
('Diana Prince', 'diana@example.com', '2026-03-12', 'Organic');

-- STREAMING_CHUNK: Inserting seed data into Orders...
INSERT INTO orders (user_id, order_date, status, gross_amount, discount_amount) VALUES
(1, '2026-02-01 10:00:00', 'completed', 150.00, 15.00),
(1, '2026-02-15 14:30:00', 'completed', 200.00, 0.00),
(2, '2026-02-25 09:15:00', 'refunded', 50.00, 5.00),
(3, '2026-03-10 16:45:00', 'completed', 300.00, 50.00),
(4, '2026-03-15 11:20:00', 'pending', 120.00, 0.00);