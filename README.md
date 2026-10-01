# RentDrive — Car Rental Reservation & Vehicle Return Management System

A fully functional Flask + MySQL web application built on your existing
`car_rental_db` database, for DBMS Project Review 2.

## Modules Implemented
- **Dashboard** — fleet KPIs, active rentals, today's pickups, this month's revenue
- **Branches, Vehicle Categories, Vehicles, Rate Plans, Customers** — full CRUD
- **Reservations** — create bookings with automatic overlap/double-booking prevention
- **Rentals** — Pickup workflow (odometer, fuel %, condition inspection) and
  Return workflow (odometer, fuel %, condition, damage line items)
- **Automatic Billing** — on return, the system calculates:
  - Rental charge = (days × daily_rate) + (km driven × per_km_rate), pulled from
    the active `rateplan` row for the vehicle's category
  - Fuel charge = (fuel % missing) × ₹50/% (configurable in `config.py`)
  - Damage charge = sum of repair costs entered
  - Generates the `invoice` row automatically and flips the vehicle to
    `AVAILABLE` (or `MAINTENANCE` if damage was reported)
- **Invoices & Payments** — view charge breakdown, record partial/full payments,
  live balance tracking
- **Reports** — monthly revenue, category demand, top customers, branch
  performance, and live fleet status (using your existing `vw_fleet_status` view)

## Setup

1. **Install dependencies**
   ```
   pip install flask mysql-connector-python
   ```

2. **Point it at your database.** Edit `config.py`:
   ```python
   DB_CONFIG = {
       "host": "localhost",
       "user": "root",
       "password": "YOUR_MYSQL_PASSWORD",   # <-- put your real password here
       "database": "car_rental_db",
   }
   ```
   Since your `car_rental_db` already has all 13 tables and the
   `vw_fleet_status` view (as shown in your `SHOW TABLES` output), you do
   **not** need to run `schema.sql`. It's included only as a reference /
   fresh-install option.

3. **(Optional) Add sample data** if your tables are empty, so you have
   something to demo:
   ```
   mysql -u root -p car_rental_db < sample_data.sql
   ```

4. **Run the app**
   ```
   python app.py
   ```
   Then open **http://127.0.0.1:5000** in your browser.

## Project Structure
```
car_rental_webapp/
├── app.py                 # Flask entry point, blueprint registration
├── config.py               # DB credentials + business rule constants
├── db.py                   # MySQL connection helper
├── schema.sql               # Reference schema (matches your existing DB)
├── sample_data.sql          # Optional demo data
├── blueprints/               # One module per feature (dashboard, vehicles, rentals, etc.)
├── templates/                 # Jinja2 + Bootstrap 5 HTML templates
└── static/css/style.css        # Custom styling
```

## Business Rules (for your viva / documentation)
- A reservation cannot be created for a vehicle that already has a `BOOKED`
  reservation with overlapping dates (checked via a date-range overlap query).
- A rental's billing rate is looked up from `rateplan` using the vehicle's
  `category_id` and the **most recent** `effective_from` date that is on or
  before the pickup date — this supports rate changes over time without
  breaking old invoices.
- Minimum rental duration for billing is 1 day, even for same-day returns.
- If any damage is logged during return inspection, the vehicle is set to
  `MAINTENANCE` instead of `AVAILABLE` — it won't show up as bookable again
  until you manually mark it available after repairs.
- All multi-table writes (pickup, return + billing) run inside a single
  database transaction, so a failure partway through rolls back cleanly
  instead of leaving inconsistent data (e.g. a rental with no invoice).

## What I tested before handing this over
Every route was exercised end-to-end against a live MySQL instance: all list/
detail/form pages, reservation creation + double-booking rejection, full
pickup → return → invoice → payment lifecycle (billing math verified exact),
odometer validation, and foreign-key delete protection. No errors or
tracebacks in any of it.
