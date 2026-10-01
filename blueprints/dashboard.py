from flask import Blueprint, render_template
from db import query, query_one

bp = Blueprint("dashboard", __name__, url_prefix="/")


@bp.route("/")
def index():
    fleet = query_one("""
        SELECT
          COUNT(*) AS total,
          SUM(status='AVAILABLE') AS available,
          SUM(status='RENTED') AS rented,
          SUM(status='MAINTENANCE') AS maintenance
        FROM vehicle
    """)

    active_rentals = query_one("""
        SELECT COUNT(*) AS c FROM rental WHERE return_date IS NULL
    """)["c"]

    todays_pickups = query_one("""
        SELECT COUNT(*) AS c FROM reservation
        WHERE status='BOOKED' AND start_date = CURDATE()
    """)["c"]

    month_revenue = query_one("""
        SELECT COALESCE(SUM(total_amount),0) AS total
        FROM invoice
        WHERE MONTH(invoice_date)=MONTH(CURDATE()) AND YEAR(invoice_date)=YEAR(CURDATE())
    """)["total"]

    recent_reservations = query("""
        SELECT r.reservation_id, c.name AS customer_name, v.reg_number, v.model,
               r.start_date, r.end_date, r.status
        FROM reservation r
        JOIN customer c ON r.customer_id = c.customer_id
        JOIN vehicle v ON r.vehicle_id = v.vehicle_id
        ORDER BY r.created_at DESC
        LIMIT 8
    """)

    ongoing_rentals = query("""
        SELECT rt.rental_id, v.reg_number, v.model, c.name AS customer_name, rt.pickup_date
        FROM rental rt
        JOIN reservation r ON rt.reservation_id = r.reservation_id
        JOIN vehicle v ON r.vehicle_id = v.vehicle_id
        JOIN customer c ON r.customer_id = c.customer_id
        WHERE rt.return_date IS NULL
        ORDER BY rt.pickup_date DESC
        LIMIT 8
    """)

    return render_template("dashboard/index.html",
                            fleet=fleet,
                            active_rentals=active_rentals,
                            todays_pickups=todays_pickups,
                            month_revenue=month_revenue,
                            recent_reservations=recent_reservations,
                            ongoing_rentals=ongoing_rentals)
