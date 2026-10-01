import mysql.connector
from mysql.connector import Error
from flask import g, current_app
from config import DB_CONFIG


def get_db():
    """Returns a MySQL connection stored on Flask's application context `g`,
    reused for the lifetime of a single request."""
    if "db" not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None and db.is_connected():
        db.close()


def query(sql, params=None, fetch=True, dictionary=True):
    """Run a SQL statement. fetch=True returns rows (list of dicts by default).
    fetch=False is for INSERT/UPDATE/DELETE and returns the lastrowid instead."""
    conn = get_db()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        cursor.execute(sql, params or ())
        if fetch:
            rows = cursor.fetchall()
            return rows
        else:
            conn.commit()
            return cursor.lastrowid
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()


def query_one(sql, params=None):
    rows = query(sql, params, fetch=True)
    return rows[0] if rows else None


def init_app(app):
    app.teardown_appcontext(close_db)
