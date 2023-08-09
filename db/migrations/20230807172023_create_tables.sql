-- migrate:up

-- Create Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    customer_xid VARCHAR(50) NOT NULL UNIQUE,
    token VARCHAR(50) NOT NULL
);

-- Create Wallet Table
CREATE TABLE wallet (
    id SERIAL PRIMARY KEY,
    amount INT,
    customer_xid VARCHAR(50) NOT NULL UNIQUE,
    enabled_at TIME,
    is_enabled BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (customer_xid) REFERENCES users (customer_xid)
);

-- Create Transactions Table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    amount INT,
    final_amount INT,
    status VARCHAR(50),
    transaction_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    transaction_from VARCHAR(50) NOT NULL,
    transaction_to VARCHAR(50) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    reference_id VARCHAR(50),
);

-- migrate:down

-- Drop Transactions Table
DROP TABLE IF EXISTS transactions;

-- Drop Wallet Table
DROP TABLE IF EXISTS wallet;

-- Drop Users Table
DROP TABLE IF EXISTS users;

