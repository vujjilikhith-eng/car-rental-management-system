USE car_rental_db;

INSERT INTO branch (branch_name, city, phone) VALUES
('Banjara Hills Branch', 'Hyderabad', '9840000001'),
('Gachibowli Branch', 'Hyderabad', '9840000002'),
('Whitefield Branch', 'Bengaluru', '9840000003');

INSERT INTO vehiclecategory (category_name, seating_capacity) VALUES
('Hatchback', 5),
('Sedan', 5),
('SUV', 7),
('Luxury', 5);

INSERT INTO rateplan (category_id, daily_rate, per_km_rate, effective_from) VALUES
(1, 1200.00, 8.00, '2026-01-01'),
(2, 1800.00, 10.00, '2026-01-01'),
(3, 2500.00, 12.00, '2026-01-01'),
(4, 4500.00, 18.00, '2026-01-01');

INSERT INTO vehicle (reg_number, category_id, branch_id, model, year_made, status) VALUES
('TS09AB1234', 1, 1, 'Maruti Swift', 2023, 'AVAILABLE'),
('TS09AB1235', 2, 1, 'Honda City', 2023, 'AVAILABLE'),
('TS09AB1236', 3, 2, 'Hyundai Creta', 2024, 'AVAILABLE'),
('TS09AB1237', 4, 2, 'Toyota Camry', 2024, 'AVAILABLE'),
('KA05CD5678', 2, 3, 'Hyundai Verna', 2023, 'MAINTENANCE');

INSERT INTO customer (name, licence_number, licence_expiry, phone, email) VALUES
('Arjun Rao', 'TS09920230001', '2030-05-10', '9000011111', 'arjun.rao@example.com'),
('Sneha Kumar', 'TS09920230002', '2029-11-22', '9000022222', 'sneha.kumar@example.com'),
('Vikram Reddy', 'AP09920220003', '2028-03-15', '9000033333', 'vikram.reddy@example.com');

INSERT INTO reservation (customer_id, vehicle_id, branch_id, start_date, end_date, status) VALUES
(1, 1, 1, '2026-09-10', '2026-09-13', 'COMPLETED'),
(2, 2, 1, '2026-09-20', '2026-09-22', 'BOOKED');

INSERT INTO rental (reservation_id, pickup_date, return_date, pickup_odometer, return_odometer, pickup_branch_id, return_branch_id) VALUES
(1, '2026-09-10 09:00:00', '2026-09-13 18:00:00', 15000, 15320, 1, 1);

INSERT INTO fuelreading (rental_id, reading_type, fuel_level_pct, reading_date) VALUES
(1, 'PICKUP', 100, '2026-09-10 09:00:00'),
(1, 'RETURN', 80, '2026-09-13 18:00:00');

INSERT INTO inspection (rental_id, inspection_type, inspection_date, condition_rating, notes) VALUES
(1, 'PICKUP', '2026-09-10 09:00:00', 'EXCELLENT', 'No visible damage'),
(1, 'RETURN', '2026-09-13 18:00:00', 'GOOD', 'Minor scratch on bumper');

INSERT INTO damage (rental_id, description, repair_cost, reported_date) VALUES
(1, 'Minor scratch on rear bumper', 800.00, '2026-09-13');

INSERT INTO invoice (rental_id, rental_charge, damage_charge, fuel_charge, total_amount, invoice_date) VALUES
(1, 3600.00, 800.00, 1000.00, 5400.00, '2026-09-13');

INSERT INTO payment (invoice_id, amount_paid, payment_date, payment_mode) VALUES
(1, 5400.00, '2026-09-13', 'UPI');
