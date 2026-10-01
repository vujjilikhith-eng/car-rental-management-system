from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import query, query_one

bp = Blueprint("categories", __name__, url_prefix="/categories")


@bp.route("/")
def index():
    categories = query("""
        SELECT vc.*,
          (SELECT COUNT(*) FROM vehicle v WHERE v.category_id = vc.category_id) AS vehicle_count
        FROM vehiclecategory vc ORDER BY vc.category_id
    """)
    return render_template("categories/index.html", categories=categories)


@bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        query(
            "INSERT INTO vehiclecategory (category_name, seating_capacity) VALUES (%s,%s)",
            (request.form["category_name"], request.form["seating_capacity"]),
            fetch=False,
        )
        flash("Category added.", "success")
        return redirect(url_for("categories.index"))
    return render_template("categories/form.html", category=None)


@bp.route("/<int:category_id>/edit", methods=["GET", "POST"])
def edit(category_id):
    if request.method == "POST":
        query(
            "UPDATE vehiclecategory SET category_name=%s, seating_capacity=%s WHERE category_id=%s",
            (request.form["category_name"], request.form["seating_capacity"], category_id),
            fetch=False,
        )
        flash("Category updated.", "success")
        return redirect(url_for("categories.index"))
    category = query_one("SELECT * FROM vehiclecategory WHERE category_id=%s", (category_id,))
    return render_template("categories/form.html", category=category)


@bp.route("/<int:category_id>/delete", methods=["POST"])
def delete(category_id):
    try:
        query("DELETE FROM vehiclecategory WHERE category_id=%s", (category_id,), fetch=False)
        flash("Category deleted.", "success")
    except Exception:
        flash("Cannot delete this category — it is referenced by vehicles or rate plans.", "error")
    return redirect(url_for("categories.index"))
