from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import query, query_one

bp = Blueprint("vehicles", __name__, url_prefix="/vehicles")


@bp.route("/")
def index():
    branch_id = request.args.get("branch_id", type=int)
    status = request.args.get("status")

    sql = """
        SELECT v.*, vc.category_name, b.branch_name
        FROM vehicle v
        JOIN vehiclecategory vc ON v.category_id = vc.category_id
        JOIN branch b ON v.branch_id = b.branch_id
        WHERE 1=1
    """
    params = []
    if branch_id:
        sql += " AND v.branch_id = %s"
        params.append(branch_id)
    if status:
        sql += " AND v.status = %s"
        params.append(status)
    sql += " ORDER BY v.vehicle_id"

    vehicles = query(sql, params)
    branches = query("SELECT * FROM branch ORDER BY branch_name")
    return render_template("vehicles/index.html", vehicles=vehicles, branches=branches,
                            selected_branch=branch_id, selected_status=status)


@bp.route("/new", methods=["GET", "POST"])
def new():
    categories = query("SELECT * FROM vehiclecategory ORDER BY category_name")
    branches = query("SELECT * FROM branch ORDER BY branch_name")
    if request.method == "POST":
        query(
            """INSERT INTO vehicle (reg_number, category_id, branch_id, model, year_made, status)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (request.form["reg_number"], request.form["category_id"], request.form["branch_id"],
             request.form["model"], request.form["year_made"], request.form["status"]),
            fetch=False,
        )
        flash("Vehicle added.", "success")
        return redirect(url_for("vehicles.index"))
    return render_template("vehicles/form.html", vehicle=None, categories=categories, branches=branches)


@bp.route("/<int:vehicle_id>/edit", methods=["GET", "POST"])
def edit(vehicle_id):
    categories = query("SELECT * FROM vehiclecategory ORDER BY category_name")
    branches = query("SELECT * FROM branch ORDER BY branch_name")
    if request.method == "POST":
        query(
            """UPDATE vehicle SET reg_number=%s, category_id=%s, branch_id=%s, model=%s,
               year_made=%s, status=%s WHERE vehicle_id=%s""",
            (request.form["reg_number"], request.form["category_id"], request.form["branch_id"],
             request.form["model"], request.form["year_made"], request.form["status"], vehicle_id),
            fetch=False,
        )
        flash("Vehicle updated.", "success")
        return redirect(url_for("vehicles.index"))
    vehicle = query_one("SELECT * FROM vehicle WHERE vehicle_id=%s", (vehicle_id,))
    return render_template("vehicles/form.html", vehicle=vehicle, categories=categories, branches=branches)


@bp.route("/<int:vehicle_id>/delete", methods=["POST"])
def delete(vehicle_id):
    try:
        query("DELETE FROM vehicle WHERE vehicle_id=%s", (vehicle_id,), fetch=False)
        flash("Vehicle deleted.", "success")
    except Exception:
        flash("Cannot delete this vehicle — it has reservation/rental history.", "error")
    return redirect(url_for("vehicles.index"))
