-- Create the database (if not exists)
CREATE DATABASE IF NOT EXISTS MovieBookingsDB;
USE MovieBookingsDB;

-- Drop tables if they already exist (to avoid conflicts)
DROP TABLE IF EXISTS order_tracking;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS movies;

-- Table: movies (stores movie details)
CREATE TABLE movies (
    movie_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_name VARCHAR(100) NOT NULL,
    time_slot TIME NOT NULL,
    price DECIMAL(5,2) NOT NULL
);

-- Insert movie records
INSERT INTO movies (movie_name, time_slot, price) VALUES
('Oh Kadhal Kanmani', '18:00:00', 150.00),
('Dear Comrade', '20:00:00', 180.00),
('Raanjhanaa', '19:30:00', 160.00),
('Loveyatri', '21:00:00', 140.00),
('Oru Kal Oru Kannadi', '17:00:00', 120.00),
('Siva Manasula Sakthi', '19:00:00', 130.00),
('Varuthapadatha Valibar Sangam', '20:30:00', 140.00),
('Boss Engira Bhaskaran', '22:00:00', 160.00),
('Vampire Diaries', '18:30:00', 200.00),
('The Originals', '21:30:00', 220.00),
('The Legacy', '19:45:00', 190.00);

-- Table: orders (stores order details)
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    no_of_tickets INT NOT NULL,
    seat_number VARCHAR(10) NOT NULL, -- New column for seat number
    total_price DECIMAL(6,2) NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
);

-- Insert sample orders with seat numbers
INSERT INTO orders (movie_id, no_of_tickets, seat_number, total_price) VALUES
(1, 2, 'A1', 300.00), -- Oh Kadhal Kanmani (2 tickets, Seat A1)
(3, 1, 'B3', 160.00), -- Raanjhanaa (1 ticket, Seat B3)
(5, 4, 'C7', 480.00); -- Oru Kal Oru Kannadi (4 tickets, Seat C7)

-- Table: order_tracking (tracks order status)
CREATE TABLE order_tracking (
    order_id INT PRIMARY KEY,
    status VARCHAR(20) DEFAULT 'Pending', -- Track order status (Pending, Confirmed, Cancelled)
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- Insert sample order tracking records
INSERT INTO order_tracking (order_id, status) VALUES
(1, 'Confirmed'),
(2, 'Pending'),
(3, 'Cancelled');

-- Fetch complete order details dynamically
SELECT o.order_id, m.movie_name, o.seat_number, m.time_slot, o.no_of_tickets, o.total_price, t.status
FROM orders o
JOIN movies m ON o.movie_id = m.movie_id
JOIN order_tracking t ON o.order_id = t.order_id
WHERE o.order_id = ?; -- Replace 1 with any order ID
