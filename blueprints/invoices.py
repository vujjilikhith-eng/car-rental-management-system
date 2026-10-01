from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import query, query_one

bp = Blueprint("invoices", __name__, url_prefix="/invoices")


@bp.route("/")
def index():
    invoices = query("""
        SELECT i.*, v.reg_number, c.name AS customer_name,
               COALESCE((SELECT SUM(p.amount_paid) FROM payment p WHERE p.invoice_id = i.invoice_id), 0) AS paid_amount
        FROM invoice i
        JOIN rental rt ON i.rental_id = rt.rental_id
        JOIN reservation r ON rt.reservation_id = r.reservation_id
        JOIN vehicle v ON r.vehicle_id = v.vehicle_id
        JOIN customer c ON r.customer_id = c.customer_id
        ORDER BY i.invoice_date DESC
    """)
    return render_template("invoices/index.html", invoices=invoices)


@bp.route("/<int:invoice_id>")
def detail(invoice_id):
    invoice = query_one("""
        SELECT i.*, rt.rental_id, v.reg_number, v.model, c.name AS customer_name, c.phone
        FROM invoice i
        JOIN rental rt ON i.rental_id = rt.rental_id
        JOIN reservation r ON rt.reservation_id = r.reservation_id
        JOIN vehicle v ON r.vehicle_id = v.vehicle_id
        JOIN customer c ON r.customer_id = c.customer_id
        WHERE i.invoice_id = %s
    """, (invoice_id,))
    payments = query("SELECT * FROM payment WHERE invoice_id=%s ORDER BY payment_date", (invoice_id,))
    paid_amount = sum(float(p["amount_paid"]) for p in payments)
    balance = float(invoice["total_amount"]) - paid_amount
    return render_template("invoices/detail.html", invoice=invoice, payments=payments,
                            paid_amount=paid_amount, balance=balance)


@bp.route("/<int:invoice_id>/pay", methods=["POST"])
def record_payment(invoice_id):
    amount = float(request.form["amount_paid"])
    mode = request.form["payment_mode"]
    query(
        """INSERT INTO payment (invoice_id, amount_paid, payment_date, payment_mode)
           VALUES (%s,%s,%s,%s)""",
        (invoice_id, amount, date.today(), mode),
        fetch=False,
    )
    flash(f"Payment of ₹{amount:.2f} recorded.", "success")
    return redirect(url_for("invoices.detail", invoice_id=invoice_id))
