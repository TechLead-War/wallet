-- migrate:up

-- Create Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    customer_xid VARCHAR(50) NOT NULL,
    token VARCHAR(50) NOT NULL
);

-- Create Wallet Table
CREATE TABLE wallet (
    id SERIAL PRIMARY KEY,
    amount INT,
    customer_xid VARCHAR(50) NOT NULL,
    enabled_at TIME,
    is_enabled BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (customer_xid) REFERENCES users (customer_xid)
);

-- Create Transactions Table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    amount INT,
    status VARCHAR(50),
    transaction_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    transaction_from VARCHAR(50) NOT NULL,
    transaction_to VARCHAR(50) NOT NULL,
    reference_id VARCHAR(50),
    FOREIGN KEY (transaction_from) REFERENCES users (customer_xid),
    FOREIGN KEY (transaction_to) REFERENCES users (customer_xid)
);

-- migrate:down

-- Drop Transactions Table
DROP TABLE IF EXISTS transactions;

-- Drop Wallet Table
DROP TABLE IF EXISTS wallet;

-- Drop Users Table
DROP TABLE IF EXISTS users;
