"""
Database configuration.
Edit these values to match your local MySQL setup.
"""

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",   # <-- change this
    "database": "car_rental_db",
}

# Business rule constants (used in billing calculations)
FUEL_CHARGE_PER_PERCENT_MISSING = 50.00   # currency units charged per % of fuel missing on return
SECRET_KEY = "car-rental-dbms-project-secret-key"
