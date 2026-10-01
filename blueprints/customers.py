from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import query, query_one

bp = Blueprint("customers", __name__, url_prefix="/customers")


@bp.route("/")
def index():
    q = request.args.get("q", "").strip()
    if q:
        customers = query(
            """SELECT * FROM customer
               WHERE name LIKE %s OR licence_number LIKE %s OR phone LIKE %s
               ORDER BY customer_id""",
            (f"%{q}%", f"%{q}%", f"%{q}%"),
        )
    else:
        customers = query("SELECT * FROM customer ORDER BY customer_id")
    return render_template("customers/index.html", customers=customers, q=q)


@bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        query(
            """INSERT INTO customer (name, licence_number, licence_expiry, phone, email)
               VALUES (%s,%s,%s,%s,%s)""",
            (request.form["name"], request.form["licence_number"], request.form["licence_expiry"],
             request.form["phone"], request.form.get("email") or None),
            fetch=False,
        )
        flash("Customer registered.", "success")
        return redirect(url_for("customers.index"))
    return render_template("customers/form.html", customer=None)


@bp.route("/<int:customer_id>/edit", methods=["GET", "POST"])
def edit(customer_id):
    if request.method == "POST":
        query(
            """UPDATE customer SET name=%s, licence_number=%s, licence_expiry=%s, phone=%s, email=%s
               WHERE customer_id=%s""",
            (request.form["name"], request.form["licence_number"], request.form["licence_expiry"],
             request.form["phone"], request.form.get("email") or None, customer_id),
            fetch=False,
        )
        flash("Customer updated.", "success")
        return redirect(url_for("customers.index"))
    customer = query_one("SELECT * FROM customer WHERE customer_id=%s", (customer_id,))
    return render_template("customers/form.html", customer=customer)


@bp.route("/<int:customer_id>/delete", methods=["POST"])
def delete(customer_id):
    try:
        query("DELETE FROM customer WHERE customer_id=%s", (customer_id,), fetch=False)
        flash("Customer deleted.", "success")
    except Exception:
        flash("Cannot delete this customer — they have reservation history.", "error")
    return redirect(url_for("customers.index"))


@bp.route("/<int:customer_id>")
def detail(customer_id):
    customer = query_one("SELECT * FROM customer WHERE customer_id=%s", (customer_id,))
    reservations = query("""
        SELECT r.*, v.reg_number, v.model
        FROM reservation r JOIN vehicle v ON r.vehicle_id = v.vehicle_id
        WHERE r.customer_id=%s ORDER BY r.start_date DESC
    """, (customer_id,))
    return render_template("customers/detail.html", customer=customer, reservations=reservations)
