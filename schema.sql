-- Car Rental Reservation & Vehicle Return Management System
-- Schema reference (matches the existing car_rental_db database).
-- Run this ONLY if you are setting the database up fresh.
-- If car_rental_db already exists with data, skip this file.

CREATE DATABASE IF NOT EXISTS car_rental_db;
USE car_rental_db;

CREATE TABLE branch (
    branch_id   INT AUTO_INCREMENT PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    city        VARCHAR(50)  NOT NULL,
    phone       VARCHAR(15)  NOT NULL,
    INDEX (branch_name)
);

CREATE TABLE customer (
    customer_id    INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    licence_number VARCHAR(30)  NOT NULL UNIQUE,
    licence_expiry DATE NOT NULL,
    phone          VARCHAR(15)  NOT NULL,
    email          VARCHAR(100)
);

CREATE TABLE vehiclecategory (
    category_id      INT AUTO_INCREMENT PRIMARY KEY,
    category_name    VARCHAR(50) NOT NULL UNIQUE,
    seating_capacity INT NOT NULL
);

CREATE TABLE vehicle (
    vehicle_id  INT AUTO_INCREMENT PRIMARY KEY,
    reg_number  VARCHAR(20) NOT NULL UNIQUE,
    category_id INT NOT NULL,
    branch_id   INT NOT NULL,
    model       VARCHAR(50) NOT NULL,
    year_made   INT NOT NULL,
    status      ENUM('AVAILABLE','RENTED','MAINTENANCE') NOT NULL DEFAULT 'AVAILABLE',
    FOREIGN KEY (category_id) REFERENCES vehiclecategory(category_id),
    FOREIGN KEY (branch_id)   REFERENCES branch(branch_id)
);

CREATE TABLE rateplan (
    rate_plan_id   INT AUTO_INCREMENT PRIMARY KEY,
    category_id    INT NOT NULL,
    daily_rate     DECIMAL(10,2) NOT NULL,
    per_km_rate    DECIMAL(10,2) NOT NULL,
    effective_from DATE NOT NULL,
    FOREIGN KEY (category_id) REFERENCES vehiclecategory(category_id)
);

CREATE TABLE reservation (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id    INT NOT NULL,
    vehicle_id     INT NOT NULL,
    branch_id      INT NOT NULL,
    start_date     DATE NOT NULL,
    end_date       DATE NOT NULL,
    status         ENUM('BOOKED','CANCELLED','COMPLETED') NOT NULL DEFAULT 'BOOKED',
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (vehicle_id)  REFERENCES vehicle(vehicle_id),
    FOREIGN KEY (branch_id)   REFERENCES branch(branch_id)
);

CREATE TABLE rental (
    rental_id        INT AUTO_INCREMENT PRIMARY KEY,
    reservation_id   INT NOT NULL UNIQUE,
    pickup_date      DATETIME NOT NULL,
    return_date      DATETIME,
    pickup_odometer  INT NOT NULL,
    return_odometer  INT,
    pickup_branch_id INT NOT NULL,
    return_branch_id INT,
    FOREIGN KEY (reservation_id)   REFERENCES reservation(reservation_id),
    FOREIGN KEY (pickup_branch_id) REFERENCES branch(branch_id),
    FOREIGN KEY (return_branch_id) REFERENCES branch(branch_id)
);

CREATE TABLE inspection (
    inspection_id    INT AUTO_INCREMENT PRIMARY KEY,
    rental_id        INT NOT NULL,
    inspection_type  ENUM('PICKUP','RETURN') NOT NULL,
    inspection_date  DATETIME NOT NULL,
    condition_rating ENUM('EXCELLENT','GOOD','FAIR','POOR') NOT NULL,
    notes            VARCHAR(255),
    FOREIGN KEY (rental_id) REFERENCES rental(rental_id)
);

CREATE TABLE fuelreading (
    fuel_reading_id INT AUTO_INCREMENT PRIMARY KEY,
    rental_id       INT NOT NULL,
    reading_type    ENUM('PICKUP','RETURN') NOT NULL,
    fuel_level_pct  INT NOT NULL,
    reading_date    DATETIME NOT NULL,
    FOREIGN KEY (rental_id) REFERENCES rental(rental_id)
);

CREATE TABLE damage (
    damage_id     INT AUTO_INCREMENT PRIMARY KEY,
    rental_id     INT NOT NULL,
    description   VARCHAR(255) NOT NULL,
    repair_cost   DECIMAL(10,2) NOT NULL,
    reported_date DATE NOT NULL,
    FOREIGN KEY (rental_id) REFERENCES rental(rental_id)
);

CREATE TABLE invoice (
    invoice_id    INT AUTO_INCREMENT PRIMARY KEY,
    rental_id     INT NOT NULL UNIQUE,
    rental_charge DECIMAL(10,2) NOT NULL,
    damage_charge DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    fuel_charge   DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total_amount  DECIMAL(10,2) NOT NULL,
    invoice_date  DATE NOT NULL,
    FOREIGN KEY (rental_id) REFERENCES rental(rental_id)
);

CREATE TABLE payment (
    payment_id   INT AUTO_INCREMENT PRIMARY KEY,
    invoice_id   INT NOT NULL,
    amount_paid  DECIMAL(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_mode ENUM('CASH','CARD','UPI','NETBANKING') NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoice(invoice_id)
);

CREATE OR REPLACE VIEW vw_fleet_status AS
SELECT v.vehicle_id, v.reg_number, v.model, vc.category_name,
       b.branch_name, v.status
FROM vehicle v
JOIN vehiclecategory vc ON v.category_id = vc.category_id
JOIN branch b ON v.branch_id = b.branch_id;
