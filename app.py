from flask import Flask
import db
from config import SECRET_KEY

from blueprints import dashboard, branches, categories, vehicles, rateplans
from blueprints import customers, reservations, rentals, invoices, reports


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    db.init_app(app)

    app.register_blueprint(dashboard.bp)
    app.register_blueprint(branches.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(vehicles.bp)
    app.register_blueprint(rateplans.bp)
    app.register_blueprint(customers.bp)
    app.register_blueprint(reservations.bp)
    app.register_blueprint(rentals.bp)
    app.register_blueprint(invoices.bp)
    app.register_blueprint(reports.bp)

    @app.template_filter("money")
    def money_format(value):
        try:
            return f"₹{float(value):,.2f}"
        except (TypeError, ValueError):
            return value

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
