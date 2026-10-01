import math
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import query, query_one, get_db
from config import FUEL_CHARGE_PER_PERCENT_MISSING

bp = Blueprint("rentals", __name__, url_prefix="/rentals")


@bp.route("/")
def index():
    status = request.args.get("status", "ongoing")
    sql = """
        SELECT rt.*, v.reg_number, v.model, c.name AS customer_name
        FROM rental rt
        JOIN reservation r ON rt.reservation_id = r.reservation_id
        JOIN vehicle v ON r.vehicle_id = v.vehicle_id
        JOIN customer c ON r.customer_id = c.customer_id
    """
    if status == "ongoing":
        sql += " WHERE rt.return_date IS NULL"
    elif status == "completed":
        sql += " WHERE rt.return_date IS NOT NULL"
    sql += " ORDER BY rt.pickup_date DESC"
    rentals = query(sql)
    return render_template("rentals/index.html", rentals=rentals, selected_status=status)


@bp.route("/<int:rental_id>")
def detail(rental_id):
    rental = query_one("""
        SELECT rt.*, r.customer_id, c.name AS customer_name, c.phone, c.licence_number,
               v.reg_number, v.model, vc.category_name, v.vehicle_id,
               pb.branch_name AS pickup_branch_name, rb.branch_name AS return_branch_name,
               r.reservation_id
        FROM rental rt
        JOIN reservation r ON rt.reservation_id = r.reservation_id
        JOIN customer c ON r.customer_id = c.customer_id
        JOIN vehicle v ON r.vehicle_id = v.vehicle_id
        JOIN vehiclecategory vc ON v.category_id = vc.category_id
        JOIN branch pb ON rt.pickup_branch_id = pb.branch_id
        LEFT JOIN branch rb ON rt.return_branch_id = rb.branch_id
        WHERE rt.rental_id = %s
    """, (rental_id,))
    fuel_readings = query("SELECT * FROM fuelreading WHERE rental_id=%s ORDER BY reading_date", (rental_id,))
    inspections = query("SELECT * FROM inspection WHERE rental_id=%s ORDER BY inspection_date", (rental_id,))
    damages = query("SELECT * FROM damage WHERE rental_id=%s", (rental_id,))
    invoice = query_one("SELECT * FROM invoice WHERE rental_id=%s", (rental_id,))
    return render_template("rentals/detail.html", rental=rental, fuel_readings=fuel_readings,
                            inspections=inspections, damages=damages, invoice=invoice)


@bp.route("/pickup/<int:reservation_id>", methods=["GET", "POST"])
def pickup(reservation_id):
    reservation = query_one("""
        SELECT r.*, c.name AS customer_name, v.reg_number, v.model, v.vehicle_id, b.branch_name
        FROM reservation r
        JOIN customer c ON r.customer_id = c.customer_id
        JOIN vehicle v ON r.vehicle_id = v.vehicle_id
        JOIN branch b ON r.branch_id = b.branch_id
        WHERE r.reservation_id = %s
    """, (reservation_id,))

    if not reservation:
        flash("Reservation not found.", "error")
        return redirect(url_for("reservations.index"))

    if reservation["status"] != "BOOKED":
        flash("This reservation is not in a BOOKED state — cannot process pickup.", "error")
        return redirect(url_for("reservations.detail", reservation_id=reservation_id))

    branches = query("SELECT * FROM branch ORDER BY branch_name")

    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()
        try:
            pickup_dt = datetime.now()
            cursor.execute(
                """INSERT INTO rental (reservation_id, pickup_date, pickup_odometer, pickup_branch_id)
                   VALUES (%s,%s,%s,%s)""",
                (reservation_id, pickup_dt, request.form["pickup_odometer"], request.form["pickup_branch_id"]),
            )
            rental_id = cursor.lastrowid

            cursor.execute(
                """INSERT INTO fuelreading (rental_id, reading_type, fuel_level_pct, reading_date)
                   VALUES (%s,'PICKUP',%s,%s)""",
                (rental_id, request.form["fuel_level_pct"], pickup_dt),
            )
            cursor.execute(
                """INSERT INTO inspection (rental_id, inspection_type, inspection_date, condition_rating, notes)
                   VALUES (%s,'PICKUP',%s,%s,%s)""",
                (rental_id, pickup_dt, request.form["condition_rating"], request.form.get("notes") or None),
            )
            cursor.execute("UPDATE vehicle SET status='RENTED' WHERE vehicle_id=%s", (reservation["vehicle_id"],))
            conn.commit()
        except Exception as e:
            conn.rollback()
            flash(f"Could not process pickup: {e}", "error")
            return redirect(url_for("reservations.detail", reservation_id=reservation_id))
        finally:
            cursor.close()

        flash("Vehicle picked up. Rental is now active.", "success")
        return redirect(url_for("rentals.detail", rental_id=rental_id))

    return render_template("rentals/pickup_form.html", reservation=reservation, branches=branches)


@bp.route("/<int:rental_id>/return", methods=["GET", "POST"])
def process_return(rental_id):
    rental = query_one("""
        SELECT rt.*, r.reservation_id, r.customer_id, r.vehicle_id, v.category_id, v.reg_number, v.model
        FROM rental rt
        JOIN reservation r ON rt.reservation_id = r.reservation_id
        JOIN vehicle v ON r.vehicle_id = v.vehicle_id
        WHERE rt.rental_id = %s
    """, (rental_id,))

    if not rental:
        flash("Rental not found.", "error")
        return redirect(url_for("rentals.index"))

    if rental["return_date"] is not None:
        flash("This rental has already been returned.", "error")
        return redirect(url_for("rentals.detail", rental_id=rental_id))

    pickup_fuel = query_one(
        "SELECT fuel_level_pct FROM fuelreading WHERE rental_id=%s AND reading_type='PICKUP'", (rental_id,)
    )["fuel_level_pct"]

    branches = query("SELECT * FROM branch ORDER BY branch_name")

    if request.method == "POST":
        return_odometer = int(request.form["return_odometer"])
        if return_odometer < rental["pickup_odometer"]:
            flash("Return odometer cannot be less than pickup odometer.", "error")
            return render_template("rentals/return_form.html", rental=rental, branches=branches,
                                    pickup_fuel=pickup_fuel)

        return_fuel = int(request.form["fuel_level_pct"])
        return_dt = datetime.now()

        # ---- Damage line items (repeated form fields: damage_desc[], damage_cost[]) ----
        descs = request.form.getlist("damage_desc")
        costs = request.form.getlist("damage_cost")
        damage_items = [
            (d.strip(), float(c)) for d, c in zip(descs, costs) if d.strip() and c.strip()
        ]

        # ---- Billing calculation ----
        rate = query_one(
            """SELECT * FROM rateplan WHERE category_id=%s AND effective_from <= %s
               ORDER BY effective_from DESC LIMIT 1""",
            (rental["category_id"], rental["pickup_date"].date()),
        )
        if not rate:
            flash("No applicable rate plan found for this vehicle's category. Add one first.", "error")
            return render_template("rentals/return_form.html", rental=rental, branches=branches,
                                    pickup_fuel=pickup_fuel)

        days = max(1, math.ceil((return_dt - rental["pickup_date"]).total_seconds() / 86400))
        km_driven = return_odometer - rental["pickup_odometer"]
        rental_charge = float(rate["daily_rate"]) * days + float(rate["per_km_rate"]) * km_driven

        fuel_missing = max(0, pickup_fuel - return_fuel)
        fuel_charge = fuel_missing * FUEL_CHARGE_PER_PERCENT_MISSING

        damage_charge = sum(c for _, c in damage_items)
        total_amount = rental_charge + fuel_charge + damage_charge

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """UPDATE rental SET return_date=%s, return_odometer=%s, return_branch_id=%s
                   WHERE rental_id=%s""",
                (return_dt, return_odometer, request.form["return_branch_id"], rental_id),
            )
            cursor.execute(
                """INSERT INTO fuelreading (rental_id, reading_type, fuel_level_pct, reading_date)
                   VALUES (%s,'RETURN',%s,%s)""",
                (rental_id, return_fuel, return_dt),
            )
            cursor.execute(
                """INSERT INTO inspection (rental_id, inspection_type, inspection_date, condition_rating, notes)
                   VALUES (%s,'RETURN',%s,%s,%s)""",
                (rental_id, return_dt, request.form["condition_rating"], request.form.get("notes") or None),
            )
            for desc, cost in damage_items:
                cursor.execute(
                    """INSERT INTO damage (rental_id, description, repair_cost, reported_date)
                       VALUES (%s,%s,%s,%s)""",
                    (rental_id, desc, cost, return_dt.date()),
                )
            cursor.execute(
                """INSERT INTO invoice (rental_id, rental_charge, damage_charge, fuel_charge, total_amount, invoice_date)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (rental_id, rental_charge, damage_charge, fuel_charge, total_amount, return_dt.date()),
            )
            invoice_id = cursor.lastrowid

            cursor.execute("UPDATE reservation SET status='COMPLETED' WHERE reservation_id=%s",
                            (rental["reservation_id"],))
            new_status = "MAINTENANCE" if damage_items else "AVAILABLE"
            cursor.execute("UPDATE vehicle SET status=%s WHERE vehicle_id=%s",
                            (new_status, rental["vehicle_id"]))
            conn.commit()
        except Exception as e:
            conn.rollback()
            flash(f"Could not process return: {e}", "error")
            return render_template("rentals/return_form.html", rental=rental, branches=branches,
                                    pickup_fuel=pickup_fuel)
        finally:
            cursor.close()

        flash(f"Return processed. Invoice #{invoice_id} generated for ₹{total_amount:.2f}.", "success")
        return redirect(url_for("invoices.detail", invoice_id=invoice_id))

    return render_template("rentals/return_form.html", rental=rental, branches=branches, pickup_fuel=pickup_fuel)
