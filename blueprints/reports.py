from flask import Blueprint, render_template, request
from db import query

bp = Blueprint("reports", __name__, url_prefix="/reports")


@bp.route("/")
def index():
    monthly_revenue = query("""
        SELECT DATE_FORMAT(invoice_date, '%Y-%m') AS month, SUM(total_amount) AS revenue, COUNT(*) AS invoice_count
        FROM invoice
        GROUP BY DATE_FORMAT(invoice_date, '%Y-%m')
        ORDER BY month DESC
        LIMIT 12
    """)

    fleet_status = query("SELECT * FROM vw_fleet_status ORDER BY branch_name, status")

    category_demand = query("""
        SELECT vc.category_name, COUNT(res.reservation_id) AS reservation_count
        FROM vehiclecategory vc
        LEFT JOIN vehicle v ON v.category_id = vc.category_id
        LEFT JOIN reservation res ON res.vehicle_id = v.vehicle_id
        GROUP BY vc.category_id, vc.category_name
        ORDER BY reservation_count DESC
    """)

    top_customers = query("""
        SELECT c.name, c.phone, COUNT(r.reservation_id) AS trip_count,
               COALESCE(SUM(i.total_amount), 0) AS total_spent
        FROM customer c
        JOIN reservation r ON r.customer_id = c.customer_id
        JOIN rental rt ON rt.reservation_id = r.reservation_id
        JOIN invoice i ON i.rental_id = rt.rental_id
        GROUP BY c.customer_id, c.name, c.phone
        ORDER BY total_spent DESC
        LIMIT 10
    """)

    branch_performance = query("""
        SELECT b.branch_name,
               COUNT(DISTINCT r.reservation_id) AS reservations,
               COALESCE(SUM(i.total_amount), 0) AS revenue
        FROM branch b
        LEFT JOIN reservation r ON r.branch_id = b.branch_id
        LEFT JOIN rental rt ON rt.reservation_id = r.reservation_id
        LEFT JOIN invoice i ON i.rental_id = rt.rental_id
        GROUP BY b.branch_id, b.branch_name
        ORDER BY revenue DESC
    """)

    return render_template("reports/index.html",
                            monthly_revenue=monthly_revenue,
                            fleet_status=fleet_status,
                            category_demand=category_demand,
                            top_customers=top_customers,
                            branch_performance=branch_performance)
