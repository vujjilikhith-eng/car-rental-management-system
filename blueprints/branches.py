from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import query, query_one

bp = Blueprint("branches", __name__, url_prefix="/branches")


@bp.route("/")
def index():
    branches = query("SELECT * FROM branch ORDER BY branch_id")
    return render_template("branches/index.html", branches=branches)


@bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        query(
            "INSERT INTO branch (branch_name, city, phone) VALUES (%s,%s,%s)",
            (request.form["branch_name"], request.form["city"], request.form["phone"]),
            fetch=False,
        )
        flash("Branch added successfully.", "success")
        return redirect(url_for("branches.index"))
    return render_template("branches/form.html", branch=None)


@bp.route("/<int:branch_id>/edit", methods=["GET", "POST"])
def edit(branch_id):
    if request.method == "POST":
        query(
            "UPDATE branch SET branch_name=%s, city=%s, phone=%s WHERE branch_id=%s",
            (request.form["branch_name"], request.form["city"], request.form["phone"], branch_id),
            fetch=False,
        )
        flash("Branch updated.", "success")
        return redirect(url_for("branches.index"))
    branch = query_one("SELECT * FROM branch WHERE branch_id=%s", (branch_id,))
    return render_template("branches/form.html", branch=branch)


@bp.route("/<int:branch_id>/delete", methods=["POST"])
def delete(branch_id):
    try:
        query("DELETE FROM branch WHERE branch_id=%s", (branch_id,), fetch=False)
        flash("Branch deleted.", "success")
    except Exception:
        flash("Cannot delete this branch — it is referenced by vehicles, reservations or rentals.", "error")
    return redirect(url_for("branches.index"))
