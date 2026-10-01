from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import query, query_one

bp = Blueprint("rateplans", __name__, url_prefix="/rateplans")


@bp.route("/")
def index():
    plans = query("""
        SELECT rp.*, vc.category_name
        FROM rateplan rp
        JOIN vehiclecategory vc ON rp.category_id = vc.category_id
        ORDER BY vc.category_name, rp.effective_from DESC
    """)
    return render_template("rateplans/index.html", plans=plans)


@bp.route("/new", methods=["GET", "POST"])
def new():
    categories = query("SELECT * FROM vehiclecategory ORDER BY category_name")
    if request.method == "POST":
        query(
            """INSERT INTO rateplan (category_id, daily_rate, per_km_rate, effective_from)
               VALUES (%s,%s,%s,%s)""",
            (request.form["category_id"], request.form["daily_rate"],
             request.form["per_km_rate"], request.form["effective_from"]),
            fetch=False,
        )
        flash("Rate plan added.", "success")
        return redirect(url_for("rateplans.index"))
    return render_template("rateplans/form.html", plan=None, categories=categories)


@bp.route("/<int:rate_plan_id>/edit", methods=["GET", "POST"])
def edit(rate_plan_id):
    categories = query("SELECT * FROM vehiclecategory ORDER BY category_name")
    if request.method == "POST":
        query(
            """UPDATE rateplan SET category_id=%s, daily_rate=%s, per_km_rate=%s, effective_from=%s
               WHERE rate_plan_id=%s""",
            (request.form["category_id"], request.form["daily_rate"],
             request.form["per_km_rate"], request.form["effective_from"], rate_plan_id),
            fetch=False,
        )
        flash("Rate plan updated.", "success")
        return redirect(url_for("rateplans.index"))
    plan = query_one("SELECT * FROM rateplan WHERE rate_plan_id=%s", (rate_plan_id,))
    return render_template("rateplans/form.html", plan=plan, categories=categories)


@bp.route("/<int:rate_plan_id>/delete", methods=["POST"])
def delete(rate_plan_id):
    try:
        query("DELETE FROM rateplan WHERE rate_plan_id=%s", (rate_plan_id,), fetch=False)
        flash("Rate plan deleted.", "success")
    except Exception:
        flash("Cannot delete this rate plan.", "error")
    return redirect(url_for("rateplans.index"))
