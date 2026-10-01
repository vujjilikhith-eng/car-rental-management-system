from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import query, query_one

bp = Blueprint("reservations", __name__, url_prefix="/reservations")


@bp.route("/")
def index():
    status = request.args.get("status")
    sql = """
        SELECT r.*, c.name AS customer_name, v.reg_number, v.model
        FROM reservation r
        JOIN customer c ON r.customer_id = c.customer_id
        JOIN vehicle v ON r.vehicle_id = v.vehicle_id
        WHERE 1=1
    """
    params = []
    if status:
        sql += " AND r.status = %s"
        params.append(status)
    sql += " ORDER BY r.created_at DESC"
    reservations = query(sql, params)
    return render_template("reservations/index.html", reservations=reservations, selected_status=status)


def _vehicle_is_available(vehicle_id, start_date, end_date, exclude_reservation_id=None):
    """Returns True if no BOOKED reservation for this vehicle overlaps the given date range."""
    sql = """
        SELECT COUNT(*) AS c FROM reservation
        WHERE vehicle_id = %s AND status = 'BOOKED'
          AND start_date <= %s AND end_date >= %s
    """
    params = [vehicle_id, end_date, start_date]
    if exclude_reservation_id:
        sql += " AND reservation_id != %s"
        params.append(exclude_reservation_id)
    row = query_one(sql, params)
    return row["c"] == 0


@bp.route("/new", methods=["GET", "POST"])
def new():
    customers = query("SELECT * FROM customer ORDER BY name")
    vehicles = query("""
        SELECT v.*, vc.category_name, b.branch_name FROM vehicle v
        JOIN vehiclecategory vc ON v.category_id=vc.category_id
        JOIN branch b ON v.branch_id=b.branch_id
        WHERE v.status='AVAILABLE'
        ORDER BY v.reg_number
    """)
    branches = query("SELECT * FROM branch ORDER BY branch_name")

    if request.method == "POST":
        vehicle_id = request.form["vehicle_id"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

        if start_date > end_date:
            flash("Start date must be before end date.", "error")
            return render_template("reservations/form.html", customers=customers,
                                    vehicles=vehicles, branches=branches)

        if not _vehicle_is_available(vehicle_id, start_date, end_date):
            flash("This vehicle is already booked for an overlapping period. Choose another vehicle or date range.", "error")
            return render_template("reservations/form.html", customers=customers,
                                    vehicles=vehicles, branches=branches)

        query(
            """INSERT INTO reservation (customer_id, vehicle_id, branch_id, start_date, end_date, status)
               VALUES (%s,%s,%s,%s,%s,'BOOKED')""",
            (request.form["customer_id"], vehicle_id, request.form["branch_id"], start_date, end_date),
            fetch=False,
        )
        flash("Reservation created.", "success")
        return redirect(url_for("reservations.index"))

    return render_template("reservations/form.html", customers=customers, vehicles=vehicles, branches=branches)


@bp.route("/<int:reservation_id>/cancel", methods=["POST"])
def cancel(reservation_id):
    query("UPDATE reservation SET status='CANCELLED' WHERE reservation_id=%s", (reservation_id,), fetch=False)
    flash("Reservation cancelled.", "success")
    return redirect(url_for("reservations.index"))


@bp.route("/<int:reservation_id>")
def detail(reservation_id):
    reservation = query_one("""
        SELECT r.*, c.name AS customer_name, c.phone, c.licence_number,
               v.reg_number, v.model, vc.category_name, b.branch_name
        FROM reservation r
        JOIN customer c ON r.customer_id = c.customer_id
        JOIN vehicle v ON r.vehicle_id = v.vehicle_id
        JOIN vehiclecategory vc ON v.category_id = vc.category_id
        JOIN branch b ON r.branch_id = b.branch_id
        WHERE r.reservation_id=%s
    """, (reservation_id,))
    rental = query_one("SELECT * FROM rental WHERE reservation_id=%s", (reservation_id,))
    return render_template("reservations/detail.html", reservation=reservation, rental=rental)
