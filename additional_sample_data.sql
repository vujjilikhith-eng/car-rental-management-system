-- Additional sample data: expands the fleet to ~20 vehicles and adds
-- several more reservations (booked / completed / cancelled) so the
-- dashboard, reports and invoices pages look fully populated for your demo.
-- Safe to run on top of your EXISTING data — uses brand-new registration
-- numbers, licence numbers and branch names so nothing collides or duplicates.

USE car_rental_db;

-- Make sure the 4 standard categories exist (skips silently if they already do)
INSERT IGNORE INTO vehiclecategory (category_name, seating_capacity) VALUES
('Hatchback', 5),
('Sedan', 5),
('SUV', 7),
('Luxury', 5);

-- Add a rate plan for any category that doesn't have one yet
INSERT INTO rateplan (category_id, daily_rate, per_km_rate, effective_from)
SELECT vc.category_id, r.daily_rate, r.per_km_rate, '2026-01-01'
FROM vehiclecategory vc
JOIN (
    SELECT 'Hatchback' AS category_name, 1200.00 AS daily_rate, 8.00 AS per_km_rate
    UNION ALL SELECT 'Sedan', 1800.00, 10.00
    UNION ALL SELECT 'SUV', 2500.00, 12.00
    UNION ALL SELECT 'Luxury', 4500.00, 18.00
) r ON r.category_name = vc.category_name
WHERE NOT EXISTS (SELECT 1 FROM rateplan rp WHERE rp.category_id = vc.category_id);

-- Two extra branches (harmless even if you already have branches with other names)
INSERT IGNORE INTO branch (branch_name, city, phone) VALUES
('Kondapur Branch', 'Hyderabad', '9840000010'),
('Miyapur Branch', 'Hyderabad', '9840000011');

-- 20 new vehicles, spread across categories and branches, all AVAILABLE
INSERT IGNORE INTO vehicle (reg_number, category_id, branch_id, model, year_made, status)
SELECT v.reg_number, vc.category_id, b.branch_id, v.model, v.year_made, 'AVAILABLE'
FROM (
    SELECT 'TS10AA0001' AS reg_number, 'Hatchback' AS category_name, 'Maruti Swift'    AS model, 2023 AS year_made, 1 AS branch_pick UNION ALL
    SELECT 'TS10AA0002', 'Hatchback', 'Hyundai i20',      2023, 2 UNION ALL
    SELECT 'TS10AA0003', 'Hatchback', 'Tata Altroz',      2024, 1 UNION ALL
    SELECT 'TS10AA0004', 'Hatchback', 'Maruti Baleno',    2022, 2 UNION ALL
    SELECT 'TS10AA0005', 'Hatchback', 'Hyundai Grand i10',2023, 1 UNION ALL
    SELECT 'TS10AB0006', 'Sedan',     'Honda City',       2023, 1 UNION ALL
    SELECT 'TS10AB0007', 'Sedan',     'Hyundai Verna',    2024, 2 UNION ALL
    SELECT 'TS10AB0008', 'Sedan',     'Skoda Slavia',     2023, 1 UNION ALL
    SELECT 'TS10AB0009', 'Sedan',     'Volkswagen Virtus',2024, 2 UNION ALL
    SELECT 'TS10AB0010', 'Sedan',     'Maruti Ciaz',      2022, 1 UNION ALL
    SELECT 'TS10AC0011', 'SUV',       'Hyundai Creta',    2024, 2 UNION ALL
    SELECT 'TS10AC0012', 'SUV',       'Mahindra XUV700',  2023, 1 UNION ALL
    SELECT 'TS10AC0013', 'SUV',       'Kia Seltos',       2024, 2 UNION ALL
    SELECT 'TS10AC0014', 'SUV',       'Tata Harrier',     2023, 1 UNION ALL
    SELECT 'TS10AC0015', 'SUV',       'Toyota Urban Cruiser', 2024, 2 UNION ALL
    SELECT 'TS10AD0016', 'Luxury',    'Toyota Camry',     2024, 1 UNION ALL
    SELECT 'TS10AD0017', 'Luxury',    'Skoda Superb',     2023, 2 UNION ALL
    SELECT 'TS10AD0018', 'Luxury',    'Honda Accord',     2024, 1 UNION ALL
    SELECT 'TS10AD0019', 'Luxury',    'BMW 3 Series',     2023, 2 UNION ALL
    SELECT 'TS10AD0020', 'Luxury',    'Audi A4',          2024, 1
) v
JOIN vehiclecategory vc ON vc.category_name = v.category_name
JOIN (
    (SELECT 1 AS pick_num, branch_id FROM branch ORDER BY branch_id LIMIT 1)
    UNION ALL
    (SELECT 2, branch_id FROM branch ORDER BY branch_id DESC LIMIT 1)
) b ON b.pick_num = v.branch_pick;

-- 6 new customers with guaranteed-unique licence numbers
INSERT IGNORE INTO customer (name, licence_number, licence_expiry, phone, email) VALUES
('Rahul Mehta', 'TS10920260101', '2031-01-15', '9600011001', 'rahul.mehta@example.com'),
('Priya Nair', 'TS10920260102', '2030-06-20', '9600011002', 'priya.nair@example.com'),
('Karan Malhotra', 'TS10920260103', '2029-09-10', '9600011003', 'karan.malhotra@example.com'),
('Divya Iyer', 'TS10920260104', '2031-03-05', '9600011004', 'divya.iyer@example.com'),
('Suresh Pillai', 'TS10920260105', '2030-12-25', '9600011005', 'suresh.pillai@example.com'),
('Meera Krishnan', 'TS10920260106', '2029-07-18', '9600011006', 'meera.krishnan@example.com');

-- 7 new reservations: 2 BOOKED (future), 1 CANCELLED, 4 COMPLETED (past, with full history)
INSERT INTO reservation (customer_id, vehicle_id, branch_id, start_date, end_date, status)
SELECT c.customer_id, v.vehicle_id, v.branch_id, r.start_date, r.end_date, r.status
FROM (
    SELECT 'TS10920260101' AS licence, 'TS10AA0001' AS reg_number, '2026-10-05' AS start_date, '2026-10-07' AS end_date, 'BOOKED' AS status UNION ALL
    SELECT 'TS10920260102', 'TS10AC0012', '2026-10-10', '2026-10-13', 'BOOKED' UNION ALL
    SELECT 'TS10920260103', 'TS10AB0006', '2026-09-25', '2026-09-27', 'CANCELLED' UNION ALL
    SELECT 'TS10920260104', 'TS10AA0002', '2026-09-01', '2026-09-03', 'COMPLETED' UNION ALL
    SELECT 'TS10920260105', 'TS10AB0007', '2026-09-05', '2026-09-08', 'COMPLETED' UNION ALL
    SELECT 'TS10920260106', 'TS10AC0013', '2026-09-10', '2026-09-12', 'COMPLETED' UNION ALL
    SELECT 'TS10920260101', 'TS10AD0016', '2026-09-15', '2026-09-17', 'COMPLETED'
) r
JOIN customer c ON c.licence_number = r.licence
JOIN vehicle v ON v.reg_number = r.reg_number;

-- For the 4 COMPLETED reservations above: create matching rental + fuel + inspection + invoice + payment
-- so Rentals / Invoices / Reports pages have real history to show.

-- Rental #1: TS10AA0002, 2 days, 180km, no damage
INSERT INTO rental (reservation_id, pickup_date, return_date, pickup_odometer, return_odometer, pickup_branch_id, return_branch_id)
SELECT r.reservation_id, '2026-09-01 09:00:00', '2026-09-03 18:00:00', 12000, 12180, r.branch_id, r.branch_id
FROM reservation r JOIN vehicle v ON r.vehicle_id = v.vehicle_id WHERE v.reg_number = 'TS10AA0002' AND r.status='COMPLETED';

INSERT INTO fuelreading (rental_id, reading_type, fuel_level_pct, reading_date)
SELECT rt.rental_id, 'PICKUP', 100, '2026-09-01 09:00:00' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AA0002'
UNION ALL
SELECT rt.rental_id, 'RETURN', 85, '2026-09-03 18:00:00' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AA0002';

INSERT INTO inspection (rental_id, inspection_type, inspection_date, condition_rating, notes)
SELECT rt.rental_id, 'PICKUP', '2026-09-01 09:00:00', 'EXCELLENT', 'No damage' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AA0002'
UNION ALL
SELECT rt.rental_id, 'RETURN', '2026-09-03 18:00:00', 'EXCELLENT', 'Returned clean' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AA0002';

INSERT INTO invoice (rental_id, rental_charge, damage_charge, fuel_charge, total_amount, invoice_date)
SELECT rt.rental_id, 2*1200 + 180*8, 0, 15*50, (2*1200 + 180*8) + (15*50), '2026-09-03'
FROM rental rt JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AA0002';

INSERT INTO payment (invoice_id, amount_paid, payment_date, payment_mode)
SELECT i.invoice_id, i.total_amount, '2026-09-03', 'UPI'
FROM invoice i JOIN rental rt ON i.rental_id = rt.rental_id JOIN reservation r ON rt.reservation_id = r.reservation_id
JOIN vehicle v ON r.vehicle_id = v.vehicle_id WHERE v.reg_number = 'TS10AA0002';

-- Update vehicle status back to AVAILABLE for the returned car
UPDATE vehicle SET status='AVAILABLE' WHERE reg_number = 'TS10AA0002';

-- Rental #2: TS10AB0007, 3 days, 300km, minor damage
INSERT INTO rental (reservation_id, pickup_date, return_date, pickup_odometer, return_odometer, pickup_branch_id, return_branch_id)
SELECT r.reservation_id, '2026-09-05 10:00:00', '2026-09-08 17:00:00', 20000, 20300, r.branch_id, r.branch_id
FROM reservation r JOIN vehicle v ON r.vehicle_id = v.vehicle_id WHERE v.reg_number = 'TS10AB0007' AND r.status='COMPLETED';

INSERT INTO fuelreading (rental_id, reading_type, fuel_level_pct, reading_date)
SELECT rt.rental_id, 'PICKUP', 100, '2026-09-05 10:00:00' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AB0007'
UNION ALL
SELECT rt.rental_id, 'RETURN', 60, '2026-09-08 17:00:00' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AB0007';

INSERT INTO inspection (rental_id, inspection_type, inspection_date, condition_rating, notes)
SELECT rt.rental_id, 'PICKUP', '2026-09-05 10:00:00', 'GOOD', 'Pre-existing minor wear' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AB0007'
UNION ALL
SELECT rt.rental_id, 'RETURN', '2026-09-08 17:00:00', 'FAIR', 'Scratch on rear door' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AB0007';

INSERT INTO damage (rental_id, description, repair_cost, reported_date)
SELECT rt.rental_id, 'Scratch on rear door', 1200.00, '2026-09-08'
FROM rental rt JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AB0007';

INSERT INTO invoice (rental_id, rental_charge, damage_charge, fuel_charge, total_amount, invoice_date)
SELECT rt.rental_id, 3*1800 + 300*10, 1200, 40*50, (3*1800 + 300*10) + 1200 + (40*50), '2026-09-08'
FROM rental rt JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AB0007';

INSERT INTO payment (invoice_id, amount_paid, payment_date, payment_mode)
SELECT i.invoice_id, i.total_amount, '2026-09-08', 'CARD'
FROM invoice i JOIN rental rt ON i.rental_id = rt.rental_id JOIN reservation r ON rt.reservation_id = r.reservation_id
JOIN vehicle v ON r.vehicle_id = v.vehicle_id WHERE v.reg_number = 'TS10AB0007';

UPDATE vehicle SET status='MAINTENANCE' WHERE reg_number = 'TS10AB0007';

-- Rental #3: TS10AC0013, 2 days, 220km, no damage
INSERT INTO rental (reservation_id, pickup_date, return_date, pickup_odometer, return_odometer, pickup_branch_id, return_branch_id)
SELECT r.reservation_id, '2026-09-10 08:30:00', '2026-09-12 19:00:00', 5000, 5220, r.branch_id, r.branch_id
FROM reservation r JOIN vehicle v ON r.vehicle_id = v.vehicle_id WHERE v.reg_number = 'TS10AC0013' AND r.status='COMPLETED';

INSERT INTO fuelreading (rental_id, reading_type, fuel_level_pct, reading_date)
SELECT rt.rental_id, 'PICKUP', 90, '2026-09-10 08:30:00' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AC0013'
UNION ALL
SELECT rt.rental_id, 'RETURN', 75, '2026-09-12 19:00:00' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AC0013';

INSERT INTO inspection (rental_id, inspection_type, inspection_date, condition_rating, notes)
SELECT rt.rental_id, 'PICKUP', '2026-09-10 08:30:00', 'GOOD', 'Normal wear' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AC0013'
UNION ALL
SELECT rt.rental_id, 'RETURN', '2026-09-12 19:00:00', 'GOOD', 'Returned in good shape' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AC0013';

INSERT INTO invoice (rental_id, rental_charge, damage_charge, fuel_charge, total_amount, invoice_date)
SELECT rt.rental_id, 2*2500 + 220*12, 0, 15*50, (2*2500 + 220*12) + (15*50), '2026-09-12'
FROM rental rt JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AC0013';

INSERT INTO payment (invoice_id, amount_paid, payment_date, payment_mode)
SELECT i.invoice_id, i.total_amount * 0.5, '2026-09-12', 'CASH'
FROM invoice i JOIN rental rt ON i.rental_id = rt.rental_id JOIN reservation r ON rt.reservation_id = r.reservation_id
JOIN vehicle v ON r.vehicle_id = v.vehicle_id WHERE v.reg_number = 'TS10AC0013';

UPDATE vehicle SET status='AVAILABLE' WHERE reg_number = 'TS10AC0013';

-- Rental #4: TS10AD0016 (Luxury), 2 days, 150km, no damage
INSERT INTO rental (reservation_id, pickup_date, return_date, pickup_odometer, return_odometer, pickup_branch_id, return_branch_id)
SELECT r.reservation_id, '2026-09-15 11:00:00', '2026-09-17 16:00:00', 8000, 8150, r.branch_id, r.branch_id
FROM reservation r JOIN vehicle v ON r.vehicle_id = v.vehicle_id WHERE v.reg_number = 'TS10AD0016' AND r.status='COMPLETED';

INSERT INTO fuelreading (rental_id, reading_type, fuel_level_pct, reading_date)
SELECT rt.rental_id, 'PICKUP', 100, '2026-09-15 11:00:00' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AD0016'
UNION ALL
SELECT rt.rental_id, 'RETURN', 90, '2026-09-17 16:00:00' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AD0016';

INSERT INTO inspection (rental_id, inspection_type, inspection_date, condition_rating, notes)
SELECT rt.rental_id, 'PICKUP', '2026-09-15 11:00:00', 'EXCELLENT', 'Spotless' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AD0016'
UNION ALL
SELECT rt.rental_id, 'RETURN', '2026-09-17 16:00:00', 'EXCELLENT', 'Returned spotless' FROM rental rt
JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AD0016';

INSERT INTO invoice (rental_id, rental_charge, damage_charge, fuel_charge, total_amount, invoice_date)
SELECT rt.rental_id, 2*4500 + 150*18, 0, 10*50, (2*4500 + 150*18) + (10*50), '2026-09-17'
FROM rental rt JOIN reservation r ON rt.reservation_id = r.reservation_id JOIN vehicle v ON r.vehicle_id = v.vehicle_id
WHERE v.reg_number = 'TS10AD0016';

INSERT INTO payment (invoice_id, amount_paid, payment_date, payment_mode)
SELECT i.invoice_id, i.total_amount, '2026-09-17', 'NETBANKING'
FROM invoice i JOIN rental rt ON i.rental_id = rt.rental_id JOIN reservation r ON rt.reservation_id = r.reservation_id
JOIN vehicle v ON r.vehicle_id = v.vehicle_id WHERE v.reg_number = 'TS10AD0016';

UPDATE vehicle SET status='AVAILABLE' WHERE reg_number = 'TS10AD0016';

-- Mark the vehicles used in the still-BOOKED future reservations as RENTED is WRONG
-- (they're only reserved, not picked up yet) — leave them AVAILABLE. No action needed.

SELECT 'Done. Fleet and reservation data expanded.' AS status;
