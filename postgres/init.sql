CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS timescaledb;
-- CREATE EXTENSION IF NOT EXISTS age;

CREATE TABLE customer (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE product (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    stock INT DEFAULT 0
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customer(id) ON DELETE CASCADE,
    order_date TIMESTAMP DEFAULT NOW(),
    total_amount NUMERIC(10,2) DEFAULT 0
);

CREATE TABLE orderline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES product(id),
    quantity INT NOT NULL,
    line_total NUMERIC(10,2) NOT NULL
);

-- Customers
INSERT INTO customer (name, email, address) VALUES
('Alice Johnson', 'alice@example.com', '123 Main St'),
('Bob Smith', 'bob@example.com', '456 Oak Ave'),
('Charlie Brown', 'charlie@example.com', '789 Pine Rd');

-- Products
INSERT INTO product (name, description, price, stock) VALUES
('Laptop', 'High-performance laptop', 1200.00, 20),
('Smartphone', 'Latest model smartphone', 800.00, 50),
('Headphones', 'Noise-canceling headphones', 150.00, 100),
('Monitor', '27-inch 4K monitor', 300.00, 30);

-- Orders
INSERT INTO orders (customer_id, total_amount) VALUES
((SELECT id FROM customer WHERE email='alice@example.com'), 1500.00),
((SELECT id FROM customer WHERE email='bob@example.com'), 800.00);

-- Orderlines
INSERT INTO orderline (order_id, product_id, quantity, line_total) VALUES
((SELECT id FROM orders LIMIT 1),
 (SELECT id FROM product WHERE name='Laptop'), 1, 1200.00),

((SELECT id FROM orders LIMIT 1),
 (SELECT id FROM product WHERE name='Headphones'), 2, 300.00),

((SELECT id FROM orders OFFSET 1 LIMIT 1),
 (SELECT id FROM product WHERE name='Smartphone'), 1, 800.00);

-- Update total amounts dynamically
UPDATE orders
SET total_amount = COALESCE((
    SELECT SUM(line_total) FROM orderline WHERE orderline.order_id = orders.id
), 0);